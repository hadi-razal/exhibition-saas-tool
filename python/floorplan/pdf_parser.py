"""
PDF Parser — Direct text extraction and page-to-image conversion.
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("exhibitiq.floorplan.pdf_parser")


class PDFParser:
    """Handles PDF text extraction and image conversion."""

    def extract_text(self, file_path: str) -> dict[int, str]:
        """
        Extract text from PDF pages using PyMuPDF and pdfplumber.
        Returns dict mapping page number (1-indexed) to text content.
        """
        pages_text = {}

        # Try PyMuPDF first (fast)
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                text = page.get_text("text")
                if text.strip():
                    pages_text[i + 1] = text
            doc.close()
            logger.info(f"PyMuPDF extracted text from {len(pages_text)} pages")
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")

        # Try pdfplumber as fallback/supplement (may get better table data)
        if not pages_text:
            try:
                import pdfplumber

                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        if text.strip():
                            pages_text[i + 1] = text

                        # Also try to extract tables
                        tables = page.extract_tables()
                        if tables:
                            table_text = ""
                            for table in tables:
                                for row in table:
                                    row_str = " | ".join(
                                        str(cell) if cell else "" for cell in row
                                    )
                                    table_text += row_str + "\n"
                            if table_text.strip():
                                existing = pages_text.get(i + 1, "")
                                pages_text[i + 1] = existing + "\n" + table_text

                logger.info(f"pdfplumber extracted text from {len(pages_text)} pages")
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}")

        return pages_text

    def convert_to_images(self, file_path: str, dpi: int = 300) -> list:
        """
        Convert PDF pages to PIL images for OCR processing.
        Returns list of PIL Image objects.
        """
        try:
            from pdf2image import convert_from_path

            images = convert_from_path(file_path, dpi=dpi)
            logger.info(f"Converted PDF to {len(images)} images at {dpi} DPI")
            return images
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            # Try with lower DPI
            try:
                from pdf2image import convert_from_path

                images = convert_from_path(file_path, dpi=150)
                logger.info(f"Converted PDF to {len(images)} images at 150 DPI (fallback)")
                return images
            except Exception as e2:
                logger.error(f"PDF to image conversion failed (fallback): {e2}")
                raise RuntimeError(
                    f"Could not convert PDF to images. Make sure poppler is installed. Error: {e2}"
                )

    def get_page_count(self, file_path: str) -> int:
        """Get the number of pages in a PDF."""
        try:
            import fitz
            doc = fitz.open(file_path)
            count = len(doc)
            doc.close()
            return count
        except Exception:
            return 0
