import fitz
import pdfplumber
import pytesseract
import requests
import trafilatura
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from trafilatura import extract as trafilatura_extract


def smart_pdf_parser(file_path: str) -> str:
    try:
        # Try extracting with PyMuPDF first
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()

        # Fallback: If text is too small, try table or OCR-based
        if len(text.strip()) < 100:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

        # Fallback again if still insufficient: Use OCR
        if len(text.strip()) < 100:
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img)

        return text.strip()
    except Exception as e:
        return f"PDF extraction failed: {str(e)}"


def smart_url_parser(url: str) -> str:
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Use trafilatura for better text extraction
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted = trafilatura_extract(downloaded)
            if extracted:
                return extracted.strip()

        # Fallback: use BeautifulSoup
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        return soup.get_text(separator="\n", strip=True)

    except Exception as e:
        return f"URL extraction failed: {str(e)}"
