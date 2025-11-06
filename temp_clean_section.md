### Document Processing Features:
- **🔍 Automatic Format Detection**: Identifies file type by extension
- **📁 Recursive Folder Scanning**: Processes documents in all subdirectories
- **📊 Metadata Preservation**: Tracks page/section/sheet information  
- **📝 Text Extraction**: Handles text, tables, and structured content
- **🛡️ Error Recovery**: Graceful handling of corrupted files
- **⚡ Batch Processing**: Processes all supported files in directory tree
- **📋 Source Citations**: References specific pages, sheets, or slides in answers

## 🔧 Technical Implementation

### Document Processing Pipeline
```
Data Directory (with subfolders) → Recursive Scan → Format Detection → Appropriate Extractor → Text + Metadata → Chunking → Embedding
```

### Format-Specific Extractors
1. **PDF**: PyMuPDF (fitz) - Page-level extraction
2. **DOCX**: python-docx - Paragraph-level extraction
3. **DOC**: PyMuPDF fallback - Page-level extraction
4. **XLSX**: openpyxl - Sheet and cell data extraction
5. **XLS**: xlrd - Legacy Excel support
6. **PPTX**: python-pptx - Slide and shape text extraction
7. **PPT**: PyMuPDF fallback - Page-level extraction

### Metadata Structures
Different document types return different metadata:
- **PDF/DOC/PPT**: `page_number`
- **DOCX**: `paragraph_number` 
- **XLSX/XLS**: `sheet_name`
- **PPTX**: `slide_number`

### Recursive Directory Scanning
The system now scans recursively through all subdirectories:
- **Pattern**: Uses `**/*{ext}` glob pattern for recursive search
- **Coverage**: Finds documents at any folder depth
- **Organization**: Supports organized folder structures like:
  ```
  data/
  ├── reports/
  │   ├── quarterly.docx
  │   └── budget.xlsx
  ├── docs/
  │   └── specifications.pdf
  └── presentations/
      └── overview.pptx
  ```