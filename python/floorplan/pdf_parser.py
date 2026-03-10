"""
PDF Parser — Direct text extraction and page-to-image conversion.

Key improvement: PyMuPDF spatial block extraction.
For vector PDFs (most professional floor plans), PyMuPDF can extract text
WITH bounding boxes, giving us spatial grouping without OCR.
"""
import logging

logger = logging.getLogger("exhibitiq.floorplan.pdf_parser")


class PDFParser:
    """Handles PDF text extraction (with spatial info) and image conversion."""

    def extract_text(self, file_path: str) -> dict[int, str]:
        """
        Extract plain text from PDF pages.
        Returns dict mapping page number (1-indexed) to text content.
        """
        pages_text = {}

        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                text = page.get_text("text")
                if text.strip():
                    pages_text[i + 1] = text
            doc.close()
            logger.info(f"PyMuPDF plain text: {len(pages_text)} pages")
        except Exception as e:
            logger.warning(f"PyMuPDF plain text failed: {e}")

        if not pages_text:
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                for row in table:
                                    text += " | ".join(
                                        str(c) if c else "" for c in row
                                    ) + "\n"
                        if text.strip():
                            pages_text[i + 1] = text
                logger.info(f"pdfplumber text: {len(pages_text)} pages")
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}")

        return pages_text

    def extract_spatial_blocks(self, file_path: str) -> dict[int, list[str]]:
        """
        Extract text blocks WITH spatial grouping from PDF using PyMuPDF.

        PyMuPDF's 'blocks' mode returns each text block (already grouped
        by proximity in the PDF layout) with its bounding box.
        For vector floor plans each booth's text is typically in its own block(s).

        Returns: {page_num: [block_text, block_text, ...]}
        """
        pages_blocks: dict[int, list[str]] = {}

        try:
            import fitz

            doc = fitz.open(file_path)
            has_content = False

            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1

                # get_text("blocks") → (x0, y0, x1, y1, text, block_no, block_type)
                # block_type 0 = text, 1 = image
                raw_blocks = page.get_text("blocks")

                text_blocks = []
                for blk in raw_blocks:
                    block_type = blk[6] if len(blk) > 6 else 0
                    if block_type != 0:
                        continue  # skip image blocks
                    text = str(blk[4]).strip()
                    if text:
                        text_blocks.append(text)

                if text_blocks:
                    pages_blocks[page_num] = text_blocks
                    has_content = True

            doc.close()

            if has_content:
                total = sum(len(b) for b in pages_blocks.values())
                logger.info(
                    f"Spatial blocks: {len(pages_blocks)} pages, {total} blocks total"
                )
                return pages_blocks

        except Exception as e:
            logger.warning(f"Spatial block extraction failed: {e}")

        return {}

    def has_embedded_text(self, file_path: str) -> bool:
        """
        Check whether a PDF has meaningful embedded text
        (vs being a pure image scan).
        Returns True if more than 20 words found across all pages.
        """
        try:
            import fitz
            doc = fitz.open(file_path)
            word_count = 0
            for page in doc:
                words = page.get_text("words")
                word_count += len(words)
                if word_count > 20:
                    doc.close()
                    return True
            doc.close()
        except Exception:
            pass
        return False

    def convert_to_images(self, file_path: str, dpi: int = 300) -> list:
        """
        Convert PDF pages to PIL images for OCR processing.
        Returns list of PIL Image objects.
        """
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, dpi=dpi)
            logger.info(f"PDF→images: {len(images)} pages at {dpi} DPI")
            return images
        except Exception as e:
            logger.warning(f"PDF→images at {dpi} DPI failed: {e}")
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(file_path, dpi=150)
                logger.info(f"PDF→images fallback: {len(images)} pages at 150 DPI")
                return images
            except Exception as e2:
                raise RuntimeError(
                    f"Cannot convert PDF to images. Ensure poppler is installed. Error: {e2}"
                )

    def get_page_count(self, file_path: str) -> int:
        try:
            import fitz
            doc = fitz.open(file_path)
            n = len(doc)
            doc.close()
            return n
        except Exception:
            return 0
