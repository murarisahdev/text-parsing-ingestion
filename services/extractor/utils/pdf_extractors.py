import fitz
import pdfplumber


def extract_with_pymupdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = "".join(page.get_text("text") for page in doc)
    doc.close()
    return text


def extract_with_pdfplumber(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def is_table_heavy(text: str) -> bool:
    lines = text.splitlines()
    return sum(1 for line in lines if "\t" in line or "  " in line) / max(len(lines), 1) > 0.4
