import os
from pathlib import Path


def load_and_chunk_file(file_path: str) -> list[str]:
    """loads pdf or text file and splits into chunks for llm processing"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"file not found: {file_path}")
    
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.pdf':
        text = load_pdf(file_path)
    elif file_extension in ['.txt', '.md']:
        text = load_text_file(file_path)
    else:
        raise ValueError(f"unsupported file type: {file_extension}")
    
    return chunk_text(text)


def load_pdf(file_path: str) -> str:
    """extracts text from pdf file"""
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("pypdf2 required for pdf processing. install with: pip install pypdf2")
    
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    
    return text.strip()


def load_text_file(file_path: str) -> str:
    """loads text from txt or md file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()


def chunk_text(text: str, chunk_size: int = 2000) -> list[str]:
    """splits text into manageable chunks"""
    if not text:
        return []
    
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        
        if current_length + word_length > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def main():
    """cli entry point for testing ingest_pdf.py"""
    import sys
    if len(sys.argv) != 2:
        print("usage: python ingest_pdf.py <file_path>")
        return
    
    file_path = sys.argv[1]
    try:
        chunks = load_and_chunk_file(file_path)
        print(f"loaded {len(chunks)} chunks from {file_path}")
        for i, chunk in enumerate(chunks[:3]):  # show first 3 chunks
            print(f"\nchunk {i+1} ({len(chunk)} chars):")
            print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    except Exception as e:
        print(f"error: {e}")


if __name__ == "__main__":
    main() 