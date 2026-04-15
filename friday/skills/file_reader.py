# skills/file_reader.py
from pathlib import Path


def read_pdf(filepath: str) -> str:
    """Extract text from a PDF file."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text[:3000] if text else "This PDF appears to be empty or image-based, Sir."
    except ImportError:
        return "PDF reading requires PyMuPDF. Run: pip install pymupdf"
    except Exception as e:
        return f"I could not read that PDF, Sir. {e}"


def read_docx(filepath: str) -> str:
    """Extract text from a Word document."""
    try:
        import docx
        doc = docx.Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text[:3000] if text else "This document appears to be empty, Sir."
    except ImportError:
        return "Word reading requires python-docx. Run: pip install python-docx"
    except Exception as e:
        return f"I could not read that document, Sir. {e}"


def read_txt(filepath: str) -> str:
    """Read a plain text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(3000)
        return content if content else "This file appears to be empty, Sir."
    except Exception as e:
        return f"I could not read that file, Sir. {e}"


def read_file(filepath: str) -> str:
    """Auto-detect file type and read it."""
    path = Path(filepath)
    if not path.exists():
        return f"I cannot find that file, Sir. Please check the path."
    ext = path.suffix.lower()
    if ext == '.pdf':
        return read_pdf(filepath)
    elif ext in ('.docx', '.doc'):
        return read_docx(filepath)
    elif ext in ('.txt', '.md', '.py', '.js', '.html', '.css'):
        return read_txt(filepath)
    else:
        return f"I am not sure how to read a {ext} file, Sir."
