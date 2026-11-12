"""
CLEARLY — OCR and Text Extraction Service
Extracts text from PDFs, images, and plain documents.
Integrates with PaddleOCR microservice or executes direct extraction.
"""

import io
from pathlib import Path
from typing import Optional
from loguru import logger
import httpx

from app.core.config import settings


class OCRService:
    def __init__(self):
        self.ocr_url = getattr(settings, "OCR_SERVICE_URL", "http://localhost:8001")

    async def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """
        Extract textual content from file bytes.
        Supports UTF-8/text files, PDFs, and image buffers.
        """
        ext = Path(filename).suffix.lower()

        # 1. Plain text or Markdown files
        if ext in (".txt", ".md", ".json", ".csv"):
            try:
                return file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return file_bytes.decode("latin-1", errors="replace")

        # 2. Try external PaddleOCR microservice if running
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                files = {"file": (filename, file_bytes, "application/octet-stream")}
                response = await client.post(f"{self.ocr_url}/ocr", files=files)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("extracted_text", "")
        except Exception:
            # Microservice is offline, continue to local extraction fallback
            pass

        # 3. Text fallback extraction for PDF if pypdf or PyPDF2 is installed
        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                text_pages = [page.extract_text() or "" for page in reader.pages]
                full_text = "\n".join(text_pages).strip()
                if full_text:
                    return full_text
            except Exception:
                pass

        # 4. Fallback if text could not be extracted via OCR
        logger.info(f"Using fallback text decoder for {filename} ({len(file_bytes)} bytes)")
        try:
            # Check for readable ASCII/UTF-8 strings within binary buffer
            printable = "".join(chr(b) if 32 <= b <= 126 or b in (10, 13) else " " for b in file_bytes[:4000])
            cleaned = " ".join(printable.split())
            if len(cleaned) > 50:
                return cleaned
        except Exception:
            pass

        return "Documento digital recibido. Contenido pendiente de procesamiento OCR especializado."


ocr_service = OCRService()

