import warnings
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

# Suppress the specific FutureWarning about encoder_attention_mask
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*", category=FutureWarning)

# Initialize model with offline capability
def get_embedder_model():
    """Get or initialize the sentence transformer model with offline support"""
    try:
        # Try to load model with local_files_only=True for offline usage
        model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        return model
    except Exception as e:
        print(f"⚠️ Warning: Could not load model in offline mode: {e}")
        try:
            # Try to load normally (may require internet for first download)
            print("📡 Attempting to download model (internet required)...")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            return model
        except Exception as e2:
            print(f"❌ Error: Could not load model: {e2}")
            print("💡 Solution: Connect to internet for first-time model download, then it will work offline.")
            raise

# Initialize model once
model = get_embedder_model()

def build_faiss_index(chunks: list[str], metadatas: list[dict], save_path: str):
    embeddings = model.encode(chunks, show_progress_bar=True)
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, f"{save_path}/index.faiss")

    with open(f"{save_path}/metadata.pkl", "wb") as f:
        pickle.dump(metadatas, f)
