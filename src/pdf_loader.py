import fitz  # PyMuPDF
from pathlib import Path
import os

def extract_text_from_pdfs(pdf_dir: str) -> list[tuple[str, str, list[dict]]]:
    """
    Extract text from PDFs with page-level metadata.
    Returns: list of (filename, full_text, page_metadata)
    """
    results = []
    pdf_dir = Path(pdf_dir)
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        # Check if file is empty or too small
        file_size = os.path.getsize(pdf_file)
        if file_size == 0:
            print(f"⚠️ Skipping empty file: {pdf_file.name}")
            continue
        elif file_size < 100:  # Files smaller than 100 bytes are likely corrupted
            print(f"⚠️ Skipping potentially corrupted file: {pdf_file.name} (size: {file_size} bytes)")
            continue
        
        try:
            doc = fitz.open(pdf_file)
            full_text = ""
            page_metadata = []
            
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                full_text += page_text
                
                # Store metadata for each page
                page_metadata.append({
                    "page_number": page_num,
                    "text": page_text,
                    "char_start": len(full_text) - len(page_text),
                    "char_end": len(full_text)
                })
            
            doc.close()
            
            # Only add to results if we extracted some text
            if full_text.strip():
                results.append((pdf_file.stem, full_text, page_metadata))
                print(f"✅ Processed: {pdf_file.name} ({len(full_text)} characters)")
            else:
                print(f"⚠️ Skipping file with no extractable text: {pdf_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {str(e)}")
            continue
    
    return results
