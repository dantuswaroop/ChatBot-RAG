#!/bin/bash

# Fast WSA Process Assistant Web Chat Startup Script
echo "🚀 Starting WSA Process Assistant (Optimized)..."
echo "================================================="

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
echo "🔄 Pre-loading models for faster startup..."

# Pre-import models to cache them
python -c "
import sys
sys.path.append('src')
print('Loading sentence transformer model...')
from retriever import get_model
model = get_model()
print('✅ Model loaded and cached!')
print('Testing generator connection...')
from generator import check_ollama_connection
if check_ollama_connection():
    print('✅ Ollama connection working!')
else:
    print('⚠️  Ollama not running - will use fallback mode')
"

echo ""
echo "🚀 Starting web interface for LAN access..."
echo "📱 The chat interface will be available on the network"
echo "🔗 Local URL: http://localhost:8501"

# Get the actual IP address - improved detection for macOS
HOST_IP=""

# Try multiple methods to get IP address
if command -v ifconfig >/dev/null 2>&1; then
    # Method 1: Get IP from active network interface (macOS/Linux)
    HOST_IP=$(ifconfig | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')
fi

# Method 2: Try hostname -I (Linux)
if [ -z "$HOST_IP" ] && command -v hostname >/dev/null 2>&1; then
    HOST_IP=$(hostname -I | awk '{print $1}' 2>/dev/null)
fi

# Method 3: Try route command (macOS)
if [ -z "$HOST_IP" ] && command -v route >/dev/null 2>&1; then
    HOST_IP=$(route get default | grep interface | awk '{print $2}' | xargs ifconfig | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}')
fi

# Method 4: Try networksetup (macOS specific)
if [ -z "$HOST_IP" ] && command -v networksetup >/dev/null 2>&1; then
    # Get active network service
    ACTIVE_SERVICE=$(networksetup -listallhardwareports | grep -A1 "Wi-Fi\|Ethernet" | grep "Device:" | head -1 | awk '{print $2}')
    if [ -n "$ACTIVE_SERVICE" ]; then
        HOST_IP=$(ifconfig "$ACTIVE_SERVICE" | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}')
    fi
fi

if [ -n "$HOST_IP" ]; then
    echo "🌐 Network URL: http://$HOST_IP:8501"
    echo ""
    echo "ℹ️  Other devices on your network can access this at:"
    echo "   http://$HOST_IP:8501"
else
    echo "🌐 Network URL: http://[FIND-YOUR-IP]:8501"
    echo ""
    echo "ℹ️  To find your IP address, try:"
    echo "   ifconfig | grep 'inet ' | grep -v '127.0.0.1'"
    echo "   or check System Preferences > Network"
fi

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
echo "🚀 Web chat is now running! Enjoy your WSA Process Assistant experience!"