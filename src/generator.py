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

def generate_intelligent_fallback_answer(query: str, context_chunks: list[dict]) -> str:
    """Generate an analytical, synthesized fallback answer when Ollama is not available"""
    if not context_chunks:
        return "No relevant information found in the provided documents to answer your question."
    
    # Collect and analyze all available content
    all_content = []
    sources = set()
    
    for chunk in context_chunks[:5]:  # Use more chunks for better analysis
        text = chunk.get('text', '').strip()
        source = chunk.get('source', 'Unknown')
        sources.add(source)
        
        if len(text) > 30:
            # Clean and structure the text
            clean_text = text.replace('\n', ' ').replace('  ', ' ').strip()
            all_content.append(clean_text)
    
    if not all_content:
        return "The retrieved content does not contain sufficient information for analysis."
    
    # Analyze query type to determine response approach
    query_lower = query.lower()
    
    # Combine all content for analysis
    combined_content = ' '.join(all_content)
    
    # Extract key concepts and terms
    query_words = set(word.lower().strip('.,!?') for word in query.split() if len(word) > 2)
    
    # Create analytical response based on query type
    if any(word in query_lower for word in ['what is', 'what are', 'define', 'explain']):
        # Definitional/explanatory questions
        response = f"Based on analysis of the documents, here's what I found:\n\n"
        
        # Look for definitions or explanations
        sentences = combined_content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 40:
                sentence_words = set(word.lower().strip('.,!?') for word in sentence.split())
                if query_words.intersection(sentence_words) and len(sentence) < 200:
                    relevant_sentences.append(sentence)
        
        if relevant_sentences:
            # Synthesize the information
            response += f"The key concept appears to be defined as: {relevant_sentences[0]}."
            if len(relevant_sentences) > 1:
                response += f" Additionally, {relevant_sentences[1]}."
        else:
            response += f"The documents contain information related to your query, but a clear definition is not explicitly provided."
    
    elif any(word in query_lower for word in ['how', 'process', 'steps', 'procedure']):
        # Process/procedure questions
        response = f"Based on the documented information, here's the process I can identify:\n\n"
        
        # Look for sequential or process information
        sentences = combined_content.split('.')
        process_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in ['first', 'then', 'next', 'step', 'process', 'procedure', 'should', 'must']):
                if len(sentence) > 30 and len(sentence) < 200:
                    process_sentences.append(sentence)
        
        if process_sentences:
            for i, step in enumerate(process_sentences[:3], 1):
                response += f"{i}. {step}.\n"
        else:
            response += "The documents mention the process but don't provide clear step-by-step details."
    
    elif any(word in query_lower for word in ['why', 'reason', 'purpose', 'benefit']):
        # Reasoning/purpose questions
        response = f"Based on the documentation, here are the key reasons and purposes:\n\n"
        
        sentences = combined_content.split('.')
        reasoning_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in ['because', 'reason', 'purpose', 'benefit', 'important', 'ensure', 'to', 'for']):
                if len(sentence) > 40 and len(sentence) < 200:
                    reasoning_sentences.append(sentence)
        
        if reasoning_sentences:
            response += f"• {reasoning_sentences[0]}.\n"
            if len(reasoning_sentences) > 1:
                response += f"• {reasoning_sentences[1]}.\n"
        else:
            response += "The documents discuss this topic but don't explicitly state the reasoning."
    
    else:
        # General questions - provide comprehensive overview
        response = f"Here's what I found in the documents regarding your question:\n\n"
        
        # Find most relevant sentences
        sentences = combined_content.split('.')
        scored_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 40:
                sentence_words = set(word.lower().strip('.,!?') for word in sentence.split())
                relevance_score = len(query_words.intersection(sentence_words))
                if relevance_score > 0:
                    scored_sentences.append((relevance_score, sentence))
        
        # Sort by relevance and take top sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        if scored_sentences:
            for i, (score, sentence) in enumerate(scored_sentences[:2]):
                response += f"• {sentence}.\n"
        else:
            response += "The documents contain related information, but I cannot extract specific details that directly answer your question."
    
    # Add source context
    if len(sources) == 1:
        response += f"\n*Analysis based on information from {list(sources)[0]}.*"
    else:
        response += f"\n*Analysis synthesized from {len(sources)} document sources.*"
    
    return response

def generate_detailed_answer(query: str, context_chunks: list[dict], model: str = "llama3") -> str:
    """
    Generate a comprehensive, synthesized answer that infers and summarizes information.
    Focuses on understanding and presenting information in a clear, accessible manner.
    """
    # Check if Ollama is available
    if not check_ollama_connection():
        return generate_intelligent_fallback_answer(query, context_chunks)
    
    # Prepare context without explicit source markers for better synthesis
    document_content = []
    source_summary = []
    
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk.get('source', 'Unknown')
        pages = chunk.get('pages', [])
        page_info = f"Pages {', '.join(map(str, pages))}" if pages else "Page unknown"
        
        document_content.append(chunk['text'])
        source_summary.append(f"• {source} ({page_info})")
    
    context = "\n\n".join(document_content)
    
    prompt = f"""You are an intelligent document analyst. Your role is to synthesize, analyze, and present information from documents in a clear, understandable manner.

ANALYSIS APPROACH:
- Read and understand the document content comprehensively
- Identify key themes, patterns, and relationships
- Synthesize information across multiple sources when relevant
- Infer logical connections and implications
- Present findings in a structured, accessible way
- Draw reasonable conclusions based on the evidence
- Explain complex concepts in simpler terms
- Identify what's important vs. what's supporting detail

RESPONSE STRUCTURE:
1. Start with a clear, direct answer to the question
2. Provide key insights and main points
3. Include relevant details that support your analysis
4. Explain any processes, relationships, or implications
5. Highlight important patterns or trends you notice
6. End with a concise summary if the topic is complex

TONE:
- Professional but accessible
- Explanatory and insightful
- Focus on helping the reader understand, not just providing facts
- Make complex information digestible

Document Content:
{context}

Question: {query}

Provide a comprehensive, analytical response that helps the reader truly understand this topic:"""

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
    """Legacy function for backward compatibility - now provides more analytical responses"""
    context = "\n".join(context_chunks)
    
    # Check if Ollama is available
    if not check_ollama_connection():
        # Convert string chunks to dict format for fallback
        dict_chunks = []
        for i, chunk in enumerate(context_chunks):
            dict_chunks.append({
                'text': chunk,
                'source': f'Document_{i+1}',
                'pages': [1]
            })
        return generate_intelligent_fallback_answer(query, dict_chunks)
    
    prompt = f"""You are an intelligent document analyst who synthesizes information to help users understand complex topics.

ANALYSIS APPROACH:
- Read and comprehensively understand all document content
- Identify key themes, relationships, and patterns
- Synthesize information across sources
- Infer logical connections and implications
- Present findings in an accessible, understandable way
- Draw reasonable conclusions based on evidence
- Explain processes and relationships clearly
- Focus on helping users understand, not just listing facts

RESPONSE GUIDELINES:
- Start with a clear, comprehensive answer
- Explain key concepts and their relationships
- Include relevant details that build understanding
- Identify important patterns or trends
- Make complex information digestible
- Use examples from the documents when helpful
- Structure your response logically

Document content:
{context}

Question: {query}

Provide an analytical, synthesized response that helps the reader understand this topic comprehensively:"""

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
        # Convert string chunks to dict format for fallback
        dict_chunks = []
        for i, chunk in enumerate(context_chunks):
            dict_chunks.append({
                'text': chunk,
                'source': f'Document_{i+1}',
                'pages': [1]
            })
        return generate_intelligent_fallback_answer(query, dict_chunks) + "\n\n⚠️ *Note: Using analytical fallback due to AI service timeout.*"
    except Exception as e:
        # Convert string chunks to dict format for fallback  
        dict_chunks = []
        for i, chunk in enumerate(context_chunks):
            dict_chunks.append({
                'text': chunk,
                'source': f'Document_{i+1}',
                'pages': [1]
            })
        return generate_intelligent_fallback_answer(query, dict_chunks) + f"\n\n⚠️ *Note: Using analytical fallback. AI service error: {str(e)}*"
