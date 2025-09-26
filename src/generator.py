import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
REQUEST_TIMEOUT = 120  # Increased to 120 second timeout for better reliability

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def generate_fallback_answer(query: str, context_chunks: list[dict]) -> str:
    """Generate a precise, document-focused fallback answer when Ollama is not available"""
    if not context_chunks:
        return "No relevant information found in the provided documents to answer your question."
    
    # Extract the most relevant content and create a direct response
    relevant_content = []
    
    for chunk in context_chunks[:2]:  # Use top 2 most relevant chunks
        text = chunk.get('text', '').strip()
        if len(text) > 50:
            # Clean and prepare the text
            clean_text = text.replace('\n', ' ').replace('  ', ' ').strip()
            
            # Extract key sentences that relate to the query
            sentences = clean_text.split('.')
            query_words = set(word.lower() for word in query.split() if len(word) > 2)
            
            best_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30:  # Substantial content
                    sentence_words = set(word.lower() for word in sentence.split())
                    # Check relevance
                    if query_words.intersection(sentence_words) or not best_sentences:
                        best_sentences.append(sentence)
                        if len(best_sentences) >= 2:
                            break
            
            relevant_content.extend(best_sentences)
    
    if relevant_content:
        # Create a direct, document-based response
        content_text = '. '.join(relevant_content[:2])
        
        # Check for yes/no questions
        if any(word in query.lower() for word in ['is', 'are', 'does', 'do', 'can', 'will', 'should']):
            if any(positive in content_text.lower() for positive in ['yes', 'required', 'must', 'shall', 'should']):
                response = f"Yes. According to the documents: {content_text}"
            elif any(negative in content_text.lower() for negative in ['no', 'not', 'cannot', 'forbidden']):
                response = f"No. According to the documents: {content_text}"
            else:
                response = f"Based on the documents: {content_text}"
        else:
            response = f"According to the documents: {content_text}"
        
        # Ensure proper ending
        if not response.endswith('.'):
            response += '.'
        
        # Keep it concise - shorter limit
        if len(response) > 250:
            response = response[:247] + '...'
        
        return response
    else:
        return "The retrieved content does not contain sufficient information to answer your question based on the available documents."

def generate_detailed_answer(query: str, context_chunks: list[dict], model: str = "llama3") -> str:
    """
    Generate a detailed answer with references and examples.
    Falls back to simple text assembly if Ollama is not available.
    """
    # Check if Ollama is available
    if not check_ollama_connection():
        return generate_fallback_answer(query, context_chunks)
    
    # Prepare context with source information
    context_with_sources = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk.get('source', 'Unknown')
        pages = chunk.get('pages', [])
        page_info = f"Pages {', '.join(map(str, pages))}" if pages else "Page unknown"
        
        context_with_sources.append(
            f"[Source {i}: {source} - {page_info}]\n{chunk['text']}\n"
        )
    
    context = "\n".join(context_with_sources)
    
    prompt = f"""You are a precise document assistant. Your job is to provide accurate, concise answers based ONLY on the provided document content.

STRICT INSTRUCTIONS:
- Answer ONLY based on the provided document content
- DO NOT add information not found in the documents
- DO NOT make assumptions or recommendations
- For yes/no questions, answer with a clear "Yes" or "No" followed by the specific document evidence
- Keep answers short and direct
- If the information is not in the documents, say "This information is not found in the provided documents"
- Quote relevant text from documents when possible
- Do not elaborate beyond what the documents state

Context from documents:
{context}

Question: {query}

Provide a precise, document-based answer:"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.Timeout:
        return generate_fallback_answer(query, context_chunks) + "\n\n⚠️ *Note: Using simplified response due to AI service timeout.*"
    except Exception as e:
        return generate_fallback_answer(query, context_chunks) + f"\n\n⚠️ *Note: Using simplified response. AI service error: {str(e)}*"


def generate_answer(query: str, context_chunks: list[str], model: str = "llama3") -> str:
    """Legacy function for backward compatibility with precise, document-focused responses"""
    context = "\n".join(context_chunks)
    prompt = f"""You are a precise document assistant. Answer ONLY based on the provided document content.

INSTRUCTIONS:
- Stick strictly to document content
- Do not hallucinate or add external information
- For yes/no questions, give definitive answers with document evidence
- Keep answers concise and direct
- If not in documents, say "Information not found in provided documents"

Document content:
{context}

Question: {query}

Document-based answer:"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"I'm having trouble accessing the information right now. Please try again in a moment. (Technical issue: {e})"
