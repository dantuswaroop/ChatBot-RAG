def chunk_text_with_metadata(text: str, page_metadata: list[dict], max_tokens: int = 512, overlap_tokens: int = 50) -> list[dict]:
    """
    Chunk text while preserving page number information with improved chunking strategy.
    
    Args:
        text: The text to chunk
        page_metadata: Metadata about page boundaries
        max_tokens: Maximum tokens per chunk (increased from 256 to 512)
        overlap_tokens: Number of tokens to overlap between chunks for context continuity
    
    Returns:
        List of chunk dictionaries with metadata.
    """
    import re
    
    # Split on sentence boundaries but also consider paragraph breaks
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_char_pos = 0
    
    for i, sentence in enumerate(sentences):
        current_chunk.append(sentence)
        sentence_length = len(sentence) + 1  # +1 for space
        
        current_token_count = len(" ".join(current_chunk).split())
        
        # Create chunk when we exceed max_tokens or reach a natural break
        should_chunk = (
            current_token_count > max_tokens or 
            (current_token_count > max_tokens * 0.7 and  # At least 70% full
             i < len(sentences) - 1 and  # Not the last sentence
             (sentences[i+1].strip().startswith(('•', '-', '1.', '2.', '3.', 'a)', 'b)', 'c)')) or  # Next sentence starts a list
              sentence.endswith((':')) or  # Current sentence ends with colon (likely introduces a list)
              len(sentences[i+1]) > 100))  # Next sentence is substantial (new topic)
        )
        
        if should_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_start = current_char_pos - len(chunk_text)
            chunk_end = current_char_pos
            
            # Find which pages this chunk spans
            chunk_pages = []
            for page_info in page_metadata:
                if (chunk_start < page_info["char_end"] and 
                    chunk_end > page_info["char_start"]):
                    # Handle different metadata structures from different document types
                    page_ref = (page_info.get("page_number") or 
                               page_info.get("paragraph_number") or 
                               page_info.get("sheet_name") or 
                               page_info.get("slide_number") or 
                               "Unknown")
                    chunk_pages.append(page_ref)
            
            chunks.append({
                "text": chunk_text,
                "pages": chunk_pages,
                "char_start": chunk_start,
                "char_end": chunk_end
            })
            
            # Create overlap for context continuity
            if overlap_tokens > 0 and current_chunk:
                overlap_words = " ".join(current_chunk).split()
                if len(overlap_words) > overlap_tokens:
                    overlap_text = " ".join(overlap_words[-overlap_tokens:])
                    current_chunk = [overlap_text]
                else:
                    current_chunk = []
            else:
                current_chunk = []
        
        current_char_pos += sentence_length
    
    # Handle remaining chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunk_start = current_char_pos - len(chunk_text)
        chunk_end = current_char_pos
        
        chunk_pages = []
        for page_info in page_metadata:
            if (chunk_start < page_info["char_end"] and 
                chunk_end > page_info["char_start"]):
                # Handle different metadata structures from different document types
                page_ref = (page_info.get("page_number") or 
                           page_info.get("paragraph_number") or 
                           page_info.get("sheet_name") or 
                           page_info.get("slide_number") or 
                           "Unknown")
                chunk_pages.append(page_ref)
        
        chunks.append({
            "text": chunk_text,
            "pages": chunk_pages,
            "char_start": chunk_start,
            "char_end": chunk_end
        })
    
    return chunks


def chunk_text(text: str, max_tokens: int = 512) -> list[str]:
    """Legacy function for backward compatibility with improved chunk size"""
    import re

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)
        if len(" ".join(current_chunk).split()) > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
