# utils.py
import pdfplumber, io, textwrap
from pathlib import Path
from transformers import pipeline
from functools import lru_cache

MAX_CHARS = 4096

@lru_cache(maxsize=1)
def get_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text(file_bytes: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif suffix == ".docx":
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return file_bytes.decode("utf-8", errors="ignore")

def chunk_text(text: str, max_chars: int = MAX_CHARS):
    wrapper = textwrap.TextWrapper(width=max_chars, break_long_words=False, break_on_hyphens=False)
    chunks = wrapper.wrap(text)
    return chunks or [text]