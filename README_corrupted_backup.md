# 🤖 Multi-Format Document Chat Assistant

A powerful Retrieval-Augmented Generation (RAG) system that allows you to chat with your documents in multiple formats (PDF, DOCX, XLSX, PPTX, and more) through multiple interfaces: web chat, command line, and interactive terminal. Uses **Ollama** for local AI inference and **FAISS** for fast document retrieval.

## ✨ Features

- **📄 Multi-Format Support**: Extract and process PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT documents
- **🔍 Smart Retrieval**: Uses FAISS for fast semantic search with configurable context chunks
- **🧠 Local AI**: Powered by Ollama for private, offline AI responses
- **💬 Multiple Interfaces**: 
  - Modern Streamlit web interface with real-time chat
  - Flask web interface with REST API
  - Command line interface for quick queries
  - Interactive terminal chat mode
- **📚 Source Tracking**: Shows exact page numbers and document sources
- **🎯 Context-Aware**: Maintains conversation context for follow-up questions
- **🌐 Network Ready**: LAN access for team collaboration
- **⚡ Performance**: Optimized startup with model caching and fallback mode

## 📄 Supported Document Formats

| Format | Extension | Library Used | Metadata Extracted |
|--------|-----------|-------------|-------------------|
| **PDF Documents** | `.pdf` | PyMuPDF (fitz) | Page numbers |
| **Word Documents** | `.docx` | python-docx | Paragraph numbers |
| **Legacy Word** | `.doc` | PyMuPDF | Page numbers |
| **Excel Spreadsheets** | `.xlsx` | openpyxl | Sheet names |
| **Legacy Excel** | `.xls` | xlrd | Sheet names |
| **PowerPoint** | `.pptx` | python-pptx | Slide numbers |
| **Legacy PowerPoint** | `.ppt` | PyMuPDF | Slide numbers |

### Document Processing Features:
- **🔍 Automatic Format Detection**: Identifies file type by extension
- **📊 Metadata Preservation**: Tracks page/section/sheet information  
- **📝 Text Extraction**: Handles text, tables, and structured content
- **🛡️ Error Recovery**: Graceful handling of corrupted files
- **⚡ Batch Processing**: Processes all supported files in a directory
- **📋 Source Citations**: References specific pages, sheets, or slides in answers

## �️ Prerequisites

Before setting up the project, ensure you have:

### Required Software
- **Python 3.8+** (tested with Python 3.12)
- **Ollama** for local AI inference
- **Git** for cloning the repository

### System Requirements
- **macOS/Linux/Windows** (instructions for all platforms)
- **4GB+ RAM** (8GB+ recommended for better performance)
- **2GB+ disk space** for models and embeddings

## 📦 Installation Guide

### Step 1: Install Ollama

#### macOS
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or using Homebrew
brew install ollama
```

#### Linux
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download the installer from [ollama.ai](https://ollama.ai) and run it.

### Step 2: Start Ollama and Install Models

```bash
# Start Ollama service (run in a separate terminal)
ollama serve

# In another terminal, install required models
ollama pull llama3.2:3b
# OR for better quality (requires more RAM):
# ollama pull llama3.1:8b

# Verify installation
ollama list
```

### Step 3: Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url>
cd rag-pdf

# Create virtual environment
python3 -m venv rag_env

# Activate virtual environment
# On macOS/Linux:
source rag_env/bin/activate
# On Windows:
# rag_env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Test Ollama connection
python -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags')
    print('✅ Ollama is running and accessible')
    print('Available models:', [model['name'] for model in response.json()['models']])
except:
    print('❌ Ollama is not running. Please start with: ollama serve')
"

# Test Python dependencies
python -c "
import streamlit, faiss, sentence_transformers, requests
print('✅ All Python dependencies installed successfully')
"
```

## 🚀 Quick Start

### 1. Prepare Your Documents

Place your PDF files in the `data/` directory:
```bash
mkdir -p data
# Copy your PDF files to the data directory
cp /path/to/your/pdfs/*.pdf data/
```

### 2. Build Knowledge Base

```bash
# Process PDFs and create embeddings (first time setup)
python src/app.py --build

# This will:
# - Extract text from all PDFs in data/
# - Create text chunks with overlap for better context
# - Generate embeddings using sentence transformers
# - Build FAISS index for fast retrieval
```

### 3. Start Chatting!

#### Option A: Streamlit Web Interface (Recommended)
```bash
# Quick start with optimized loading
./start_web_chat_fast.sh

# Or standard start
./start_web_chat.sh

# Or manually:
streamlit run src/web_chat.py
```
**Access at:** http://localhost:8501

**For LAN Access (team use):**
```bash
# The fast script automatically enables LAN access
./start_web_chat_fast.sh
# Access from any device on your network at: http://[YOUR-IP]:8501
```

#### Option B: Flask Web Interface
```bash
# Start Flask web chat
./start_flask_chat.sh

# Or manually:
cd src && python flask_chat.py
```
**Access at:** http://localhost:5000

#### Option C: Command Line Interface
```bash
# Ask a single question
python src/app.py --ask "What is the main topic of the documents?"

# Start interactive terminal chat
python src/app.py --chat

# Example questions:
python src/app.py --ask "What are the security requirements?"
python src/app.py --ask "Summarize the main policies"
```

## 🌐 Network Access & Team Collaboration

### LAN Access Setup
```bash
# Start with LAN access enabled
./start_web_chat_fast.sh

# The script will show:
# 🌐 Network URL: http://192.168.1.100:8501
# ℹ️  Other devices on your network can access this at:
#    http://192.168.1.100:8501
```

### Firewall Configuration
If team members can't access the web interface:

**macOS:**
```bash
# Allow incoming connections on port 8501
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/python
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /path/to/python
```

**Linux:**
```bash
# Open port 8501
sudo ufw allow 8501
```

**Windows:**
Add a firewall rule to allow Python through Windows Defender Firewall.

## 💡 Usage Guide

### Web Interface Features

#### Streamlit Interface
- **Interactive Chat**: Real-time conversation with document context
- **Context Chunks Slider**: Adjust how many document pieces to use (3-10)
  - **3-4 chunks**: Fast responses, focused answers
  - **5-6 chunks**: Balanced performance (recommended)
  - **7-10 chunks**: Comprehensive answers, slower processing
- **Source References**: Click to see exact document locations
- **Chat History**: Maintains conversation context
- **Mobile Responsive**: Works on tablets and phones

#### Context Chunks Explained
The "Number of context chunks" setting controls how the AI answers your questions:
- **What it does**: Retrieves the most relevant text pieces from your documents
- **How it works**: More chunks = more context but slower responses
- **Recommendation**: Start with 5, increase for complex questions

### Command Line Tips
```bash
# Quick queries
python src/app.py --ask "What is the approval process?"

# Interactive mode with context
python src/app.py --chat
# Then ask follow-up questions naturally

# Rebuild index after adding new PDFs
python src/app.py --build
```
./start_web_chat.sh

# Or manually:
streamlit run src/web_chat.py
```
Access at: http://localhost:8501

#### Option B: Flask Web Interface
```bash
# Start Flask web chat
./start_flask_chat.sh

# Or manually:
cd src && python flask_chat.py
```
Access at: http://localhost:5000

#### Option C: Command Line
```bash
# Ask a single question
python src/app.py --ask "What is the main topic of the documents?"

# Start interactive terminal chat
python src/app.py --chat
```

## 🖥️ Web Chat Interfaces

### Streamlit Interface
- Modern, interactive UI with real-time updates
- Sidebar with document info and settings
- Chat history persistence
- Expandable context viewer
- Mobile-responsive design

### Flask Interface
- Clean, professional web interface
- RESTful API backend
- Real-time status monitoring
- Responsive chat bubbles
- Source highlighting

## 📁 Project Structure

```
rag-pdf/
├── src/
│   ├── app.py              # Main CLI application & build pipeline
│   ├── web_chat.py         # Streamlit web interface (primary)
│   ├── flask_chat.py       # Flask web interface (alternative)
│   ├── pdf_loader.py       # PDF text extraction with PyMuPDF
│   ├── chunker.py          # Text chunking with overlap (512 tokens)
│   ├── embedder.py         # FAISS index creation & management
│   ├── retriever.py        # Semantic search with sentence transformers
│   ├── generator.py        # Ollama integration & answer generation
│   ├── config.py           # Configuration settings
│   └── templates/
│       ├── index.html      # Flask main template
│       └── chat.html       # Flask chat template
├── data/                   # PDF documents (place your files here)
│   ├── *.pdf              # Your PDF documents
├── embeddings/             # Generated FAISS index & metadata
│   ├── index.faiss         # FAISS vector database
│   └── metadata.pkl        # Document metadata & chunk info
├── rag_env/                # Python virtual environment
├── requirements.txt        # Python dependencies
├── start_web_chat.sh       # Standard Streamlit launcher
├── start_web_chat_fast.sh  # Optimized launcher with LAN support
├── start_flask_chat.sh     # Flask launcher
├── README.md               # This documentation
└── FORMATTING_FEATURES.md  # Response formatting guide
```

## ⚙️ System Configuration

### Performance Tuning
```bash
# Optimize for your system
# Low-end systems (4GB RAM):
ollama pull llama3.2:1b
# Edit src/generator.py: model = "llama3.2:1b"

# Mid-range systems (8GB RAM):
ollama pull llama3.2:3b  # Default recommendation

# High-end systems (16GB+ RAM):
ollama pull llama3.1:8b
# Better quality, slower responses
```

### Startup Scripts Explained
- **`start_web_chat_fast.sh`**: Optimized for quick startup, LAN access, model pre-loading
- **`start_web_chat.sh`**: Standard launch, local access only
- **`start_flask_chat.sh`**: Alternative Flask interface

## 🛠️ Usage Examples & Best Practices

### Document Format Examples

The system can now process multiple document formats. Here are examples of what you can query:

#### PDF Documents
```bash
"What are the security policies mentioned in the PDF?"
"Summarize the risk management procedures from page 15"
```

#### Word Documents (.docx/.doc)
```bash
"What sections are covered in the Word document?"
"Extract the requirements from the specification document"
```

#### Excel Spreadsheets (.xlsx/.xls)
```bash
"What products are listed in the spreadsheet?"
"Show me the budget breakdown from the Excel file"
"What data is in the Summary sheet?"
```

#### PowerPoint Presentations (.pptx/.ppt)
```bash
"What are the main features mentioned in the presentation?"
"Summarize the slides about project timeline"
"What conclusions are drawn in the final slides?"
```

### Effective Question Patterns
```bash
# Good question examples:
"What are the security requirements for software development?"
"Summarize the risk assessment process"
"What documentation is needed for compliance audit?"
"How should code reviews be conducted?"

# For detailed responses, use keywords like:
"Explain in detail the threat modeling process"
"Provide comprehensive information about..."
"Give me all details on..."
```

### Web Interface Tips
- **Context Chunks**: Start with 5, adjust based on question complexity
- **Follow-up Questions**: The system maintains conversation context
- **Source Navigation**: Click source references to see exact document locations
- **Chat History**: Conversations persist during your session

### Command Line Efficiency
```bash
# Quick answers
python src/app.py --ask "What is the approval workflow?"

# Interactive sessions for complex topics
python src/app.py --chat
# > What are the testing requirements?
# > Tell me more about unit testing
# > What about integration testing?
```

## � Document Management

### Supported PDF Types
- **Text-based PDFs**: Full text extraction
- **Scanned PDFs**: Requires OCR preprocessing
- **Mixed content**: Text + images (text portions processed)
- **Multi-language**: English optimized, other languages supported

### Adding New Documents
```bash
# Add PDFs to data directory
cp /path/to/new/*.pdf data/

# Rebuild knowledge base
python src/app.py --build

# Restart web interface to use new knowledge
./start_web_chat_fast.sh
```

### Document Organization Tips
- Use descriptive filenames
- Group related documents in subfolders
- Keep documents up to date
- Remove outdated versions before rebuilding

## 🔧 Customization Guide

### Response Style Modifications
Edit `src/generator.py` to customize AI behavior:
```python
# For technical documentation
SYSTEM_PROMPT = "Provide precise, technical answers with specific details and procedures."

# For general business documents  
SYSTEM_PROMPT = "Give clear, concise answers suitable for business users."

# For educational content
SYSTEM_PROMPT = "Explain concepts thoroughly with examples and context."
```

### UI Customization
Modify `src/web_chat.py` for interface changes:
- Adjust chunk slider range
- Change default settings
- Modify page layout
- Add custom styling

## 📄 License & Credits

### License
This project is open source and available under the **MIT License**.

### Dependencies & Credits
- **Ollama**: Local LLM inference engine
- **FAISS**: Facebook AI Similarity Search for vector operations
- **Streamlit**: Modern web app framework
- **Sentence Transformers**: Text embedding models
- **PyMuPDF**: PDF text extraction
- **Flask**: Alternative web framework

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Support & Community
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Share usage tips and ask questions
- **Documentation**: Help improve this README and add examples

---

## 🎯 Quick Reference Commands

```bash
# Essential commands for daily use:

# 1. First-time setup
source rag_env/bin/activate
ollama serve                          # In separate terminal
ollama pull llama3.2:3b
python src/app.py --build

# 2. Daily usage
./start_web_chat_fast.sh             # Web interface (recommended)
python src/app.py --ask "question"   # Quick CLI query  
python src/app.py --chat             # Interactive CLI

# 3. Maintenance
python src/app.py --build             # Rebuild after adding PDFs
pip install --upgrade -r requirements.txt  # Update dependencies
ollama pull llama3.2:3b              # Update AI model

# 4. Troubleshooting
curl http://localhost:11434/api/tags  # Check Ollama
python -c "import streamlit; print('OK')"  # Check dependencies
lsof -ti:8501 | xargs kill -9        # Free port if needed
```

**Happy chatting with your documents! 🚀📚**

*Transform your PDF documents into an intelligent, conversational knowledge base with the power of local AI.*

## 🔍 Troubleshooting

### Common Issues & Solutions

#### 1. **Ollama Connection Issues**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# If model not found, install it
ollama pull llama3.2:3b

# Test connection
python -c "
import requests
try:
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    print('✅ Ollama is running')
except:
    print('❌ Ollama connection failed')
"
```

#### 2. **No Embeddings Found**
```bash
# Build embeddings (first time or after adding new PDFs)
python src/app.py --build

# If build fails, check:
# - PDFs are in data/ directory
# - PDFs contain extractable text
# - Virtual environment is activated
```

#### 3. **Import/Dependency Errors**
```bash
# Ensure virtual environment is activated
source rag_env/bin/activate  # macOS/Linux
# or: rag_env\Scripts\activate  # Windows

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# If specific package fails, install individually:
pip install streamlit faiss-cpu sentence-transformers
```

#### 4. **Empty or Poor Responses**
- **Check PDFs**: Ensure they contain extractable text (not just images)
- **Verify embeddings**: Run `python src/app.py --build` again
- **Increase context chunks**: Use 7-10 chunks in web interface
- **Check Ollama model**: Try `ollama pull llama3.1:8b` for better quality

#### 5. **Web Interface Issues**
```bash
# Port already in use
# Kill process using port 8501
lsof -ti:8501 | xargs kill -9

# Permission denied (macOS/Linux)
sudo chown -R $USER:$USER rag_env/

# Can't access from other devices
# Check firewall settings and use LAN script
./start_web_chat_fast.sh
```

#### 6. **Performance Issues**
- **Slow responses**: Reduce context chunks to 3-4
- **High memory usage**: Use smaller Ollama model (`llama3.2:1b`)
- **Startup slow**: Use `./start_web_chat_fast.sh` for optimized loading

### Debug Mode & Diagnostics
```bash
# Verbose mode for detailed output
python src/app.py --build --verbose

# Test individual components
python -c "
# Test PDF loading
from src.pdf_loader import load_pdfs
pdfs = load_pdfs('data')
print(f'Loaded {len(pdfs)} PDFs')

# Test embedding creation
from src.retriever import get_model
model = get_model()
print('✅ Sentence transformer loaded')

# Test Ollama
import requests
r = requests.get('http://localhost:11434/api/tags')
print('Available models:', [m['name'] for m in r.json()['models']])
"

# Check system resources
python -c "
import psutil
print(f'RAM: {psutil.virtual_memory().percent}% used')
print(f'CPU: {psutil.cpu_percent()}% used')
"
```

### Logs & Error Investigation
```bash
# Streamlit logs
streamlit run src/web_chat.py --logger.level debug

# Check Ollama logs
# On macOS: ~/Library/Logs/ollama.log
# On Linux: ~/.ollama/logs/server.log

# Python error traces
python src/app.py --chat 2>&1 | tee debug.log
```

## 🚀 Advanced Usage

### Ollama Model Management
```bash
# List installed models
ollama list

# Install different models for various use cases
ollama pull llama3.2:1b     # Fastest, least memory
ollama pull llama3.2:3b     # Balanced (recommended)
ollama pull llama3.1:8b     # Best quality, more memory
ollama pull mistral:7b      # Alternative model

# Switch models in the application
# Edit src/generator.py and modify the model name in API calls
```

### Custom Configuration

#### Modify Chunk Settings
Edit `src/chunker.py`:
```python
# Adjust chunk size and overlap
CHUNK_SIZE = 512    # Increase for more context per chunk
OVERLAP = 50        # Increase for better context continuity
```

#### Custom Embedding Models
Edit `src/retriever.py`:
```python
# Use different sentence transformer models
MODEL_NAME = "all-MiniLM-L6-v2"           # Fast, good quality
MODEL_NAME = "all-mpnet-base-v2"          # Better quality, slower
MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"  # Balanced
```

#### LLM Prompt Customization
Edit `src/generator.py`:
```python
# Modify the system prompt for different response styles
SYSTEM_PROMPT = """
You are a helpful assistant that answers questions based on provided context.
Be concise and cite sources with page numbers.
If asked for details, provide comprehensive explanations.
"""
```

### Batch Processing & Automation
```bash
# Process multiple document sets
for dir in documents/*/; do
    echo "Processing $dir"
    cp "$dir"*.pdf data/
    python src/app.py --build
    mv embeddings/ "embeddings_$(basename "$dir")"
done

# Automated document updates
# Add to crontab for daily processing
0 2 * * * cd /path/to/rag-pdf && source rag_env/bin/activate && python src/app.py --build
```

### API Integration
Create a simple REST API wrapper:
```python
# api_server.py
from flask import Flask, request, jsonify
import sys, os
sys.path.append('src')
from app import ask_question

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def api_ask():
    data = request.json
    question = data.get('question', '')
    response, sources = ask_question(question)
    return jsonify({
        'answer': response,
        'sources': sources
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### Performance Optimization

#### Memory Management
```bash
# Monitor memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

# Optimize for low memory systems
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

#### GPU Acceleration (if available)
```bash
# Install GPU-enabled packages
pip install faiss-gpu torch torchvision torchaudio

# Verify GPU usage
python -c "
import torch
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
"
```

### Security & Privacy

#### Local-Only Setup
- **Ollama**: Runs locally, no external API calls
- **Embeddings**: Generated and stored locally
- **Documents**: Never leave your machine
- **Network**: Disable external connections if needed

#### Production Deployment
```bash
# Use gunicorn for production Flask deployment
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 src.flask_chat:app

# Use reverse proxy (nginx) for HTTPS
# Add SSL certificates for secure team access
```
    python src/app.py --build --data-dir "$dir"
done
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Happy chatting with your documents! 🚀📚**