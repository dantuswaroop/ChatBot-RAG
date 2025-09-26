#!/bin/bash

# WSA Process Assistant Flask Chat Startup Script
echo "🤖 Starting WSA Process Assistant Flask Chat..."
echo "=============================================="

# Set environment variables for offline mode
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider activating your venv:"
    echo "   source rag_env/bin/activate"
fi

# Check if embeddings exist
if [ ! -f "embeddings/index.faiss" ]; then
    echo ""
    echo "❌ No embeddings found! Building knowledge base first..."
    echo "📄 Processing PDFs and creating embeddings..."
    python src/app.py --build
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build embeddings. Please check your setup."
        exit 1
    fi
    echo "✅ Knowledge base created successfully!"
fi

echo ""
echo "🚀 Starting Flask web server..."
echo "📱 The chat interface will be available at:"
echo "🔗 URL: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================="

# Start Flask app
cd src && python flask_chat.py
