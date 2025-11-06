from flask import Flask, render_template, request, jsonify
import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing modules
from retriever import load_faiss_index, retrieve
from generator import generate_detailed_answer

app = Flask(__name__)

# Configuration
EMBEDDING_DIR = "../embeddings"
DOC_DIR = "../data"  # Renamed from PDF_DIR since we now support multiple formats

# Global variables to store the loaded index and metadata
rag_system_loaded = False
index = None
metadata = None

def load_rag_system():
    """Load the RAG system (FAISS index and metadata)"""
    global rag_system_loaded, index, metadata
    
    if not rag_system_loaded:
        try:
            # Construct the correct path to embeddings
            embedding_path = os.path.join(os.path.dirname(__file__), EMBEDDING_DIR)
            
            if not os.path.exists(os.path.join(embedding_path, "index.faiss")):
                return False, "No embeddings found! Please run the build pipeline first."
            
            index, metadata = load_faiss_index(embedding_path)
            rag_system_loaded = True
            return True, "RAG system loaded successfully!"
            
        except Exception as e:
            return False, f"Error loading RAG system: {str(e)}"
    
    return True, "RAG system already loaded."

def get_answer(query: str, top_k: int = 5):
    """Get answer from the RAG system"""
    try:
        # Retrieve relevant chunks
        relevant_chunks = retrieve(query, index, metadata, k=top_k)
        
        # Generate detailed answer
        answer = generate_detailed_answer(query, relevant_chunks)
        
        # Add source summary
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
        
        return {
            "success": True,
            "answer": answer + sources_summary,
            "sources": unique_sources,
            "relevant_chunks": len(relevant_chunks)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating answer: {str(e)}"
        }

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"success": False, "error": "No message provided"}), 400
    
    user_message = data['message'].strip()
    if not user_message:
        return jsonify({"success": False, "error": "Empty message"}), 400
    
    # Check if RAG system is loaded
    success, message = load_rag_system()
    if not success:
        return jsonify({"success": False, "error": message}), 500
    
    # Get top_k from request or use default
    top_k = data.get('top_k', 5)
    
    # Generate response
    result = get_answer(user_message, top_k)
    
    if result["success"]:
        return jsonify({
            "success": True,
            "response": result["answer"],
            "sources": result["sources"],
            "relevant_chunks": result["relevant_chunks"],
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({"success": False, "error": result["error"]}), 500

@app.route('/api/status')
def status():
    """Check system status"""
    embedding_path = os.path.join(os.path.dirname(__file__), EMBEDDING_DIR)
    doc_path = os.path.join(os.path.dirname(__file__), DOC_DIR)
    
    # Check if embeddings exist
    embeddings_exist = os.path.exists(os.path.join(embedding_path, "index.faiss"))
    
    # List all supported document files
    supported_extensions = {'.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'}
    doc_files = []
    if os.path.exists(doc_path):
        doc_files = [f for f in os.listdir(doc_path) 
                    if any(f.lower().endswith(ext) for ext in supported_extensions)]
    
    return jsonify({
        "embeddings_exist": embeddings_exist,
        "rag_system_loaded": rag_system_loaded,
        "document_files": doc_files,
        "document_count": len(doc_files),
        "supported_formats": list(supported_extensions)
    })

if __name__ == '__main__':
    print("🤖 Starting Document Chat Assistant (Flask)")
    print("=" * 60)
    print("📄 Supported formats: PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT")
    print("=" * 60)
    
    # Check if embeddings exist
    embedding_path = os.path.join(os.path.dirname(__file__), EMBEDDING_DIR)
    if not os.path.exists(os.path.join(embedding_path, "index.faiss")):
        print("❌ Warning: No embeddings found!")
        print("💡 Run 'python src/app.py --build' first to create the knowledge base.")
    else:
        print("✅ Knowledge base found!")
    
    print("🌐 Starting web server...")
    print("🔗 Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
