import faiss
import pickle
import warnings
from sentence_transformers import SentenceTransformer

# Suppress the specific FutureWarning about encoder_attention_mask
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*", category=FutureWarning)

# Global model variable to avoid reloading
_model = None

def get_model():
    """Lazy load the sentence transformer model with offline support"""
    global _model
    if _model is None:
        try:
            # Try to load model with local_files_only=True for offline usage
            _model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            print("✅ Loaded sentence transformer model (offline mode)")
        except Exception as e:
            print(f"⚠️ Warning: Could not load model in offline mode: {e}")
            try:
                # Try to load normally (may require internet for first download)
                print("📡 Attempting to download model (internet required)...")
                _model = SentenceTransformer("all-MiniLM-L6-v2")
                print("✅ Downloaded and loaded sentence transformer model")
            except Exception as e2:
                print(f"❌ Error: Could not load model: {e2}")
                print("💡 Solution: Connect to internet for first-time model download, then it will work offline.")
                raise
    return _model

def load_faiss_index(path: str):
    index = faiss.read_index(f"{path}/index.faiss")
    with open(f"{path}/metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def retrieve(query: str, index, metadata, k: int = 5):
    model = get_model()  # Use lazy loading
    query_vector = model.encode([query])
    distances, indices = index.search(query_vector, k)
    
    results = []
    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
        chunk_metadata = metadata[idx].copy()
        chunk_metadata['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
        chunk_metadata['rank'] = i + 1
        results.append(chunk_metadata)
    
    return results
