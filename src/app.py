from pdf_loader import extract_text_from_pdfs
from chunker import chunk_text, chunk_text_with_metadata
from embedder import build_faiss_index
from retriever import load_faiss_index, retrieve
from generator import generate_answer, generate_detailed_answer
import os
from pathlib import Path

PDF_DIR = "data"
EMBEDDING_DIR = "embeddings"

def run_build_pipeline():
    print("📄 Extracting PDFs with page information...")
    raw_docs = extract_text_from_pdfs(PDF_DIR)

    if not raw_docs:
        print("❌ No valid PDFs found or processed!")
        print("💡 Make sure you have non-empty PDF files in the 'data/' directory.")
        print("📋 Current data directory contents:")
        data_path = Path(PDF_DIR)
        if data_path.exists():
            for pdf_file in data_path.glob("*.pdf"):
                size = os.path.getsize(pdf_file)
                status = "✅ Valid" if size > 100 else "❌ Empty/Invalid"
                print(f"   {pdf_file.name}: {size} bytes - {status}")
        return

    all_chunks = []
    all_meta = []

    for filename, text, page_metadata in raw_docs:
        print(f"✂️ Chunking {filename} with page tracking...")
        chunks_with_meta = chunk_text_with_metadata(text, page_metadata)
        
        for chunk_info in chunks_with_meta:
            all_chunks.append(chunk_info["text"])
            all_meta.append({
                "source": filename,
                "text": chunk_info["text"],
                "pages": chunk_info["pages"],
                "char_start": chunk_info["char_start"],
                "char_end": chunk_info["char_end"]
            })

    if not all_chunks:
        print("❌ No text chunks created! PDFs may not contain extractable text.")
        return

    os.makedirs(EMBEDDING_DIR, exist_ok=True)
    print("🔗 Building FAISS index...")
    build_faiss_index(all_chunks, all_meta, EMBEDDING_DIR)

    print("✅ Embedding complete and index saved.")


def ask_question(query: str, top_k: int = 5):
    print("🔍 Retrieving relevant context...")
    index, metadata = load_faiss_index(EMBEDDING_DIR)
    relevant_chunks = retrieve(query, index, metadata, k=top_k)

    print("💬 Generating detailed answer with references...")
    answer = generate_detailed_answer(query, relevant_chunks)
    
    # Add source summary at the end
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
    
    return answer + sources_summary


def interactive_chat():
    """
    Interactive chat mode - continuously waits for user questions
    and provides detailed answers with references until the program is killed (Ctrl+C).
    """
    print("🤖 Enhanced RAG PDF Chat Assistant")
    print("=" * 60)
    print("Ask detailed questions and get comprehensive answers with:")
    print("• Specific examples from documents")
    print("• Page number references")
    print("• Multiple document sources")
    print("Type your questions and press Enter. Use Ctrl+C to exit.")
    print("=" * 60)
    
    # Check if embeddings exist
    if not os.path.exists(os.path.join(EMBEDDING_DIR, "index.faiss")):
        print("❌ No embeddings found! Please run with --build first to index your PDFs.")
        return
    
    try:
        while True:
            # Get user input
            print("\n" + "─" * 50)
            user_query = input("❓ Your question: ").strip()
            
            # Skip empty queries
            if not user_query:
                print("Please enter a valid question.")
                continue
            
            # Process the query
            try:
                print("🔄 Processing your question...")
                response = ask_question(user_query, top_k=7)  # Get more context for detailed answers
                print(f"\n🧠 **Detailed Answer:**\n{response}")
                
                # Optional: Show relevance information
                print(f"\n💡 *Tip: The answer above includes references to specific pages and documents.*")
                
            except Exception as e:
                print(f"❌ Error processing your question: {str(e)}")
                print("Please try again with a different question.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using Enhanced RAG PDF Chat Assistant. Goodbye!")
    except EOFError:
        print("\n\n👋 Chat session ended. Goodbye!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ask questions from your local PDFs using RAG + Ollama.")
    parser.add_argument("--build", action="store_true", help="Run the indexing pipeline on PDFs.")
    parser.add_argument("--ask", type=str, help="Ask a single question based on the indexed PDFs.")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode (default if no other option is provided).")

    args = parser.parse_args()

    if args.build:
        run_build_pipeline()
    elif args.ask:
        response = ask_question(args.ask)
        print(f"\n🧠 Answer:\n{response}")
    elif args.chat:
        interactive_chat()
    else:
        # Default to interactive chat mode if no arguments provided
        interactive_chat()
