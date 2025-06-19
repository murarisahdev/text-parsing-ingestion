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
        text = ""

        # 1. PyMuPDF
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            print(f"[fitz] Extracted {len(text)} characters")
        except Exception as e:
            print(f"[fitz] failed: {e}")

        # 2. pdfplumber
        if len(text.strip()) < 100:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                print(f"[pdfplumber] Extracted {len(text)} characters")
            except Exception as e:
                print(f"[pdfplumber] failed: {e}")

        # 3. OCR
        if len(text.strip()) < 100:
            print("[OCR] Trying fallback")
            try:
                images = convert_from_path(file_path)
                print(f"[OCR] {len(images)} pages converted from PDF")
                for img in images:
                    result = pytesseract.image_to_string(img)
                    print(f"[OCR] Extracted {len(result.strip())} characters from one page")
                    text += result
                print(f"[OCR] Total extracted: {len(text)} characters")
            except Exception as e:
                print(f"[OCR] failed: {e}")

        return text.strip()
    except Exception as e:
        print(f"[Parser Error] PDF extraction failed: {e}")
        return ""


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
