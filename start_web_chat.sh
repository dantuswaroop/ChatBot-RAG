#!/bin/bash

# WSA Process Assistant Web Chat Startup Script
echo "🤖 Starting WSA Process Assistant..."
echo "==========================================="

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
echo "🚀 Starting web interface for LAN access..."
echo "📱 The chat interface will be available on the network"
echo "🔗 Local URL: http://localhost:8501"
echo "🌐 Network URL: http://[YOUR-IP]:8501"
echo ""
echo "ℹ️  Other devices on your network can access this at:"
echo "   http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==========================================="

# Start Streamlit app with LAN access enabled
streamlit run src/web_chat.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.runOnSave false \
    --server.fileWatcherType none \
    --browser.gatherUsageStats false
