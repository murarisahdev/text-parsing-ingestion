import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path


def ocr_required(file_path: str) -> bool:
    doc = fitz.open(file_path)
    for page in doc:
        if len(page.get_text("text").strip()) > 50:
            return False
    return True


def run_ocr(file_path: str) -> str:
    images = convert_from_path(file_path)
    return "\n".join(pytesseract.image_to_string(img) for img in images)
