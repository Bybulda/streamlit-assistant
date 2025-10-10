import io
from pypdf import PdfReader
import docx

def extract_text_from_pdf_bytes(data: bytes) -> str:
    file_like = io.BytesIO(data)
    reader = PdfReader(file_like)
    text = []
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text.append(content)
    return "\n".join(text)


def extract_text_from_docx_bytes(data: bytes) -> str:
    file_like = io.BytesIO(data)
    doc = docx.Document(file_like)
    text = [para.text for para in doc.paragraphs]
    return "\n".join(text)


def extract_text_from_bytes(data: bytes, file_extension: str) -> str:
    ext = file_extension.lower()
    if ext == ".pdf":
        return extract_text_from_pdf_bytes(data)
    elif ext == ".docx":
        return extract_text_from_docx_bytes(data)
    elif ext in [".txt", ".md"]:
        return data.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file format: {ext}")
