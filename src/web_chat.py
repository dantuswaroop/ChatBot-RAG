import streamlit as st
import os
import sys
from datetime import datetime
import re

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing modules
from retriever import load_faiss_index, retrieve
from generator import generate_detailed_answer

# Configuration
EMBEDDING_DIR = "../embeddings"
DOC_DIR = "../data"  # Renamed from PDF_DIR since we now support multiple formats

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "rag_initialized" not in st.session_state:
        st.session_state.rag_initialized = False
    if "index" not in st.session_state:
        st.session_state.index = None
    if "metadata" not in st.session_state:
        st.session_state.metadata = None
    if "loading_complete" not in st.session_state:
        st.session_state.loading_complete = False

@st.cache_resource
def load_faiss_index_cached(embedding_path):
    """Cached version of FAISS index loading"""
    return load_faiss_index(embedding_path)

def load_rag_system():
    """Load the RAG system (FAISS index and metadata)"""
    try:
        if not st.session_state.rag_initialized:
            # Show loading message immediately
            loading_placeholder = st.empty()
            loading_placeholder.info("🔄 Loading knowledge base... This may take a moment on first load.")
            
            # Construct the correct path to embeddings
            embedding_path = os.path.join(os.path.dirname(__file__), EMBEDDING_DIR)
            
            if not os.path.exists(os.path.join(embedding_path, "index.faiss")):
                loading_placeholder.empty()
                st.error("❌ No embeddings found! Please run the build pipeline first to index your documents.")
                st.info("Run: `python src/app.py --build` to create the knowledge base.")
                return False
            
            # Load the system using cached function
            index, metadata = load_faiss_index_cached(embedding_path)
            st.session_state.index = index
            st.session_state.metadata = metadata
            st.session_state.rag_initialized = True
            st.session_state.loading_complete = True
            
            loading_placeholder.empty()
            st.success("✅ Knowledge base loaded successfully!", icon="✅")
        return True
    except Exception as e:
        st.error(f"❌ Error loading knowledge base: {str(e)}")
        return False

def get_answer(query: str, top_k: int = 5):
    """Get answer from the RAG system using the same logic as command line"""
    try:
        # Retrieve relevant chunks
        relevant_chunks = retrieve(query, st.session_state.index, st.session_state.metadata, k=top_k)
        
        if not relevant_chunks:
            return "❌ No relevant information found in the documents to answer your question.", []
        
        # Generate detailed answer (same as command line)
        answer = generate_detailed_answer(query, relevant_chunks)
        
        # Add source summary (same as command line)
        sources_summary = "\n\n📚 **Sources Used:**\n"
        unique_sources = {}
        for chunk in relevant_chunks:
            source = chunk.get('source', 'Unknown')
            pages = chunk.get('pages', [])
            if source not in unique_sources:
                unique_sources[source] = set()
            unique_sources[source].update(pages)
        
        for source, pages in unique_sources.items():
            sorted_pages = sorted(list(pages))
            if sorted_pages:
                sources_summary += f"• {source}: Pages {', '.join(map(str, sorted_pages))}\n"
            else:
                sources_summary += f"• {source}: Page information unavailable\n"
        
        # Check if user wants detailed response with structured format
        detailed_keywords = ['detailed', 'detail', 'explain in detail', 'comprehensive', 'thorough', 'elaborate', 'full explanation', 'breakdown', 'step by step']
        wants_detailed = any(keyword.lower() in query.lower() for keyword in detailed_keywords)
        
        if wants_detailed:
            # Format the response with full categories for detailed requests
            formatted_response = format_detailed_response(query, answer, relevant_chunks)
        else:
            # Use the same simple format as command line (just answer + sources)
            formatted_response = answer + sources_summary
        
        return formatted_response, relevant_chunks
        
    except Exception as e:
        return f"❌ Error generating answer: {str(e)}", []

def format_concise_response(query: str, answer: str, relevant_chunks: list) -> str:
    """Format a very concise response"""
    # Clean and shorten the answer text
    clean_answer = clean_answer_text(answer)
    
    # Make the answer even more concise
    short_answer = make_answer_concise(clean_answer)
    
    # Simple response without references
    formatted_response = f"{short_answer}"
    
    return formatted_response

def format_detailed_response(query: str, answer: str, relevant_chunks: list) -> str:
    """Format the response into detailed structured categories"""
    
    # Extract unique sources and pages
    unique_sources = {}
    for chunk in relevant_chunks:
        source = chunk.get('source', 'Unknown')
        pages = chunk.get('pages', [])
        if source not in unique_sources:
            unique_sources[source] = set()
        unique_sources[source].update(pages)
    
    # Create formatted response
    formatted_response = f"""
## 📋 **Query Analysis**
**Question:** {query}

---

## 📝 **Short Description**
{extract_summary(answer)}

---

## 📖 **Detailed Answer**
{clean_answer_text(answer)}

---

## 🔗 **Document Links & References**
"""
    
    # Add document references
    for source, pages in unique_sources.items():
        sorted_pages = sorted(list(pages))
        if sorted_pages:
            page_list = ', '.join(map(str, sorted_pages))
            formatted_response += f"**📄 {source}**\n"
            formatted_response += f"   - Pages: {page_list}\n"
            formatted_response += f"   - Relevance: High (retrieved for this query)\n\n"
        else:
            formatted_response += f"**📄 {source}**\n"
            formatted_response += f"   - Page information: Not available\n"
            formatted_response += f"   - Relevance: High (retrieved for this query)\n\n"
    
    formatted_response += """---

## 📚 **Sources Used**
"""
    
    # Add detailed source breakdown
    for i, chunk in enumerate(relevant_chunks[:3], 1):  # Top 3 most relevant
        source = chunk.get('source', 'Unknown')
        pages = chunk.get('pages', [])
        similarity = chunk.get('similarity_score', 0)
        
        page_info = f"Pages {', '.join(map(str, pages))}" if pages else "Page unknown"
        
        formatted_response += f"""
**Source {i}: {source}**
- **Location:** {page_info}
- **Relevance Score:** {similarity:.2f}
- **Content Preview:** {chunk.get('text', '')[:200]}...

"""
    
    formatted_response += f"""---

## ℹ️ **Query Metadata**
- **Total Sources Consulted:** {len(unique_sources)}
- **Relevant Chunks Retrieved:** {len(relevant_chunks)}
- **Processing Time:** Real-time
- **Confidence Level:** {'High' if len(relevant_chunks) >= 3 else 'Medium' if len(relevant_chunks) >= 2 else 'Low'}

---
*Generated by WSA Process Assistant*
"""
    
    return formatted_response

def make_answer_concise(answer: str) -> str:
    """Make the answer very concise by taking only the most essential information"""
    # Split into sentences
    sentences = answer.split('.')
    
    # Take only the first 2-3 sentences or first paragraph
    if len(sentences) > 3:
        concise = '. '.join(sentences[:3]).strip() + '.'
    else:
        concise = answer.strip()
    
    # Limit to maximum 300 characters for very short responses
    if len(concise) > 300:
        concise = concise[:297] + '...'
    
    return concise

def extract_summary(answer: str) -> str:
    """Extract a short summary from the detailed answer"""
    # Clean the answer first
    clean_answer = clean_answer_text(answer)
    
    # Take first sentence or paragraph as summary
    sentences = clean_answer.split('.')
    if sentences:
        summary = sentences[0].strip()
        if len(summary) > 150:
            summary = summary[:147] + "..."
        return summary + "."
    
    # Fallback - take first 150 characters
    if len(clean_answer) > 150:
        return clean_answer[:147] + "..."
    return clean_answer

def clean_answer_text(answer: str) -> str:
    """Clean the answer text by removing redundant source information"""
    # Remove the automatic sources summary that gets added
    if "📚 **Sources Used:**" in answer:
        answer = answer.split("📚 **Sources Used:**")[0].strip()
    
    # Remove source citations in the format [Source X: ...]
    import re
    answer = re.sub(r'\[Source \d+:.*?\]', '', answer)
    
    # Clean up extra whitespace
    answer = re.sub(r'\n\s*\n', '\n\n', answer.strip())
    
    return answer

def display_source_explorer(relevant_chunks):
    """Display the interactive source explorer"""
    st.divider()
    
    # Single column layout without stats
    with st.expander("🔍 **Explore Source Context**", expanded=False):
        # Create tabs for each unique source
        unique_sources = {}
        for chunk in relevant_chunks:
            source = chunk.get('source', 'Unknown')
            if source not in unique_sources:
                unique_sources[source] = []
            unique_sources[source].append(chunk)
        
        if len(unique_sources) > 1:
            tabs = st.tabs([f"📄 {source}" for source in unique_sources.keys()])
            
            for tab, (source, chunks) in zip(tabs, unique_sources.items()):
                with tab:
                    st.write(f"**Document:** {source}")
                    for i, chunk in enumerate(chunks, 1):
                        pages = chunk.get('pages', [])
                        similarity = chunk.get('similarity_score', 0)
                        
                        st.write(f"**Excerpt {i}** (Pages: {', '.join(map(str, pages)) if pages else 'Unknown'})")
                        st.write(f"*Relevance: {similarity:.2f}*")
                        
                        # Show text in a nice container
                        with st.container():
                            st.text_area(
                                f"Content {i}:",
                                chunk.get('text', ''),
                                height=150,
                                disabled=True,
                                key=f"chunk_{source}_{i}_{hash(chunk.get('text', ''))}"
                            )
                        
                        if i < len(chunks):
                            st.divider()
        else:
            # Single source - show all chunks
            source = list(unique_sources.keys())[0]
            chunks = unique_sources[source]
            st.write(f"**Document:** {source}")
            
            for i, chunk in enumerate(chunks, 1):
                pages = chunk.get('pages', [])
                similarity = chunk.get('similarity_score', 0)
                
                st.write(f"**Excerpt {i}** (Pages: {', '.join(map(str, pages)) if pages else 'Unknown'})")
                st.write(f"*Relevance: {similarity:.2f}*")
                
                with st.container():
                    st.text_area(
                        f"Content {i}:",
                        chunk.get('text', ''),
                        height=150,
                        disabled=True,
                        key=f"chunk_single_{i}_{hash(chunk.get('text', ''))}"
                    )
                
                if i < len(chunks):
                    st.divider()

def display_message(message, is_user=True):
    """Display a chat message"""
    if is_user:
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

def main():
    # Page configuration
    st.set_page_config(
        page_title="Document Chat Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 Document Chat Assistant")
    st.markdown("Ask questions about your documents (PDF, DOCX, XLSX, PPTX, etc.) and get detailed answers with source references!")
    
    # Show loading status if not yet loaded
    if not st.session_state.get('loading_complete', False):
        st.info("🔄 Initializing system... Please wait.")
        
    # Main chat interface - try to load RAG system
    rag_loaded = load_rag_system()
    
    # Sidebar
    with st.sidebar:
        st.header("📖 Knowledge Base Info")
        
        # Check if embeddings exist
        embedding_path = os.path.join(os.path.dirname(__file__), EMBEDDING_DIR)
        doc_path = os.path.join(os.path.dirname(__file__), DOC_DIR)
        
        if os.path.exists(os.path.join(embedding_path, "index.faiss")):
            if st.session_state.get('loading_complete', False):
                st.success("✅ Knowledge base ready")
            else:
                st.warning("🔄 Loading knowledge base...")
            
            # Show all supported document files
            if os.path.exists(doc_path):
                supported_extensions = {'.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'}
                doc_files = [f for f in os.listdir(doc_path) 
                           if any(f.lower().endswith(ext) for ext in supported_extensions)]
                if doc_files:
                    st.subheader("📄 Available Documents:")
                    for doc_file in doc_files:
                        # Show icon based on file type
                        ext = '.' + doc_file.lower().split('.')[-1]
                        icons = {
                            '.pdf': '📄', '.docx': '📝', '.doc': '📝',
                            '.xlsx': '📊', '.xls': '📊', 
                            '.pptx': '📋', '.ppt': '📋'
                        }
                        icon = icons.get(ext, '📄')
                        st.text(f"{icon} {doc_file}")
        else:
            st.error("❌ No knowledge base found")
            st.info("Run the build pipeline first:\n```bash\npython src/app.py --build\n```")
        
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        top_k = st.slider("Number of context chunks", min_value=3, max_value=10, value=5, 
                         help="Controls how many relevant text chunks are retrieved from your documents to answer each question")
        
        # Help information for chunk size
        with st.expander("📚 What does 'Number of context chunks' do?"):
            st.markdown("""
            **Context chunks** are small pieces of text from your PDF documents that are most relevant to your question.
            
            **How it works:**
            - When you ask a question, the system searches through all your documents
            - It finds the most relevant text chunks (typically 1-2 paragraphs each)
            - These chunks are sent to the AI model to generate an answer
            
            **Effect of different values:**
            - **3-4 chunks:** Fast responses, focused answers from most relevant content
            - **5-6 chunks:** Balanced performance, good context without overwhelming the AI
            - **7-10 chunks:** More comprehensive answers but slower processing
            
            **Trade-offs:**
            - **More chunks = More context** but slower response time
            - **Fewer chunks = Faster responses** but may miss some relevant information
            
            **Recommendation:** Start with 5 chunks (default) and adjust based on your needs:
            - Increase for complex questions requiring broad context
            - Decrease for simple questions or faster responses
            """)
        
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # Instructions
        st.subheader("💡 How to Use")
        st.markdown("""
        1. Place your documents in the `data/` folder
        2. **Supported formats:** PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT
        3. Run the build pipeline to create embeddings
        4. Ask questions about your documents
        5. Get detailed answers with page/section references
        """)
        
        # Sample questions
        st.subheader("❓ Sample Questions")
        st.markdown("*Add 'detailed' for comprehensive analysis*")
        sample_questions = [
            "What are the main security policies?",
            "Summarize the risk management procedures",
            "What compliance requirements are mentioned?",
            "Explain the change control process in detail",
            "What are the key objectives outlined?",
            "Give detailed training requirements"
        ]
        
        for question in sample_questions:
            if st.button(f"📝 {question}", key=f"sample_{hash(question)}", use_container_width=True):
                # Set the question in session state to be processed
                st.session_state.sample_question = question
                st.rerun()
    
    # Only show chat interface if RAG system is loaded
    if not rag_loaded:
        st.warning("⚠️ Knowledge base not ready. Please check the error messages above.")
        st.stop()
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(message, is_user=message["role"] == "user")
    
    # Handle sample question if selected
    sample_question = st.session_state.get('sample_question', None)
    if sample_question:
        # Clear the sample question from session state
        del st.session_state.sample_question
        
        # Process the sample question
        st.session_state.messages.append({"role": "user", "content": sample_question})
        display_message({"content": sample_question}, is_user=True)
        
        # Generate response for sample question
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching documents and generating answer..."):
                response, relevant_chunks = get_answer(sample_question, top_k=top_k)
            
            # Display the formatted response
            st.markdown(response)
            
            # Add interactive source explorer
            if relevant_chunks:
                display_source_explorer(relevant_chunks)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_message({"content": prompt}, is_user=True)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching documents and generating answer..."):
                response, relevant_chunks = get_answer(prompt, top_k=top_k)
            
            # Display the formatted response
            st.markdown(response)
            
            # Add interactive source explorer
            if relevant_chunks:
                display_source_explorer(relevant_chunks)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
