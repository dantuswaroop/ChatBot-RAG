#!/usr/bin/env python3

import sys
import warnings
sys.path.append('src')

print("Testing sentence transformer model loading...")

# Test the embedder
try:
    from embedder import model as embedder_model
    print("✅ Embedder model loaded successfully")
    
    # Test encoding
    test_result = embedder_model.encode(["This is a test sentence"])
    print("✅ Embedder encoding test completed")
except Exception as e:
    print(f"❌ Embedder error: {e}")

# Test the retriever
try:
    from retriever import model as retriever_model
    print("✅ Retriever model loaded successfully")
    
    # Test encoding
    test_result = retriever_model.encode(["This is another test sentence"])
    print("✅ Retriever encoding test completed")
except Exception as e:
    print(f"❌ Retriever error: {e}")

print("All tests completed!")
