"""
Floor Plan Extractor — Main orchestrator module.

Multi-layered extraction pipeline:
1. Direct PDF text extraction (PyMuPDF / pdfplumber)
2. OCR fallback for scanned/image-based content
3. Regex pattern matching for booth numbers, sizes, halls, exhibitor names
"""
import os
import re
import logging
from pathlib import Path
from typing import AsyncGenerator

from .pdf_parser import PDFParser
from .ocr_engine import OCREngine
from .pattern_matcher import PatternMatcher

logger = logging.getLogger("exhibitiq.floorplan")


class FloorPlanExtractor:
    """Orchestrates the floor plan data extraction pipeline."""

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.ocr_engine = OCREngine()
        self.pattern_matcher = PatternMatcher()

    async def extract(self, file_path: str) -> AsyncGenerator[dict, None]:
        """
        Extract structured data from a floor plan file.
        Yields SSE-compatible progress events and final results.
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        all_rows = []

        # Step 0: Upload received
        yield {"type": "progress", "step": 0, "message": "File uploaded"}

        # Step 1: Detect format
        yield {"type": "progress", "step": 1, "message": f"Detected format: {ext}"}

        try:
            if ext == ".pdf":
                # Try direct text extraction first
                yield {"type": "progress", "step": 2, "message": "Extracting PDF text..."}

                pages_text = self.pdf_parser.extract_text(file_path)
                has_text = any(text.strip() for text in pages_text.values())

                if has_text:
                    logger.info(f"Found text in {len(pages_text)} pages via direct extraction")
                    # Parse text for structured data
                    yield {"type": "progress", "step": 3, "message": "Parsing structured data from text..."}
                    for page_num, text in pages_text.items():
                        if text.strip():
                            rows = self.pattern_matcher.extract_from_text(text, page_num)
                            all_rows.extend(rows)

                # Also try OCR on pages (may find additional data)
                if not has_text or len(all_rows) < 3:
                    yield {"type": "progress", "step": 2, "message": "Running OCR on PDF pages..."}
                    try:
                        page_images = self.pdf_parser.convert_to_images(file_path)
                        for page_num, img in enumerate(page_images, 1):
                            ocr_results = self.ocr_engine.process_image(img)
                            rows = self.pattern_matcher.extract_from_text(
                                ocr_results["text"], page_num
                            )
                            # Add bounding box info if available
                            for row in rows:
                                row["source"] = "ocr"
                            all_rows.extend(rows)
                    except Exception as e:
                        logger.warning(f"OCR fallback failed: {e}")
                        if not all_rows:
                            yield {
                                "type": "progress",
                                "step": 2,
                                "message": f"OCR warning: {str(e)[:100]}",
                            }

            elif ext in [".png", ".jpg", ".jpeg"]:
                # Direct image OCR
                yield {"type": "progress", "step": 2, "message": "Running OCR on image..."}
                ocr_results = self.ocr_engine.process_image_file(file_path)

                yield {"type": "progress", "step": 3, "message": "Parsing structured data..."}
                rows = self.pattern_matcher.extract_from_text(ocr_results["text"], 1)
                for row in rows:
                    row["source"] = "ocr"
                all_rows.extend(rows)

            else:
                yield {
                    "type": "error",
                    "message": f"Unsupported file format: {ext}",
                }
                return

            # Deduplicate
            all_rows = self._deduplicate(all_rows)

            # Final result
            yield {"type": "progress", "step": 4, "message": f"Complete — {len(all_rows)} rows extracted"}
            yield {"type": "result", "rows": all_rows, "total": len(all_rows)}

        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            yield {"type": "error", "message": f"Extraction failed: {str(e)}"}

    def _deduplicate(self, rows: list[dict]) -> list[dict]:
        """Remove duplicate rows based on key fields."""
        seen = set()
        unique = []
        for row in rows:
            key = (
                row.get("booth_number", ""),
                row.get("exhibitor_name", ""),
                row.get("page", ""),
            )
            if key not in seen:
                seen.add(key)
                unique.append(row)
        return unique
