"""
Floor Plan Extractor — Main orchestrator.

Extraction pipeline (Python tools only, no external AI API):
1. For vector PDFs  → PyMuPDF spatial block extraction (text + positions)
2. For image PDFs   → pdf2image + Tesseract OCR (PSM 11, multi-pass) + spatial clustering
3. For image files  → Tesseract OCR + spatial clustering
Pattern matching works block-by-block for accurate field identification.
"""
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
        Extract structured booth data from a floor plan file.
        Yields SSE-compatible progress events and a final result event.
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        all_rows: list[dict] = []

        yield {"type": "progress", "step": 0, "message": "File uploaded successfully"}
        yield {"type": "progress", "step": 1, "message": f"Detected format: {ext.upper()}"}

        try:
            if ext == ".pdf":
                # --- Phase 1: Try spatial block extraction (vector PDFs) ---
                yield {"type": "progress", "step": 2, "message": "Extracting text layout from PDF..."}

                if self.pdf_parser.has_embedded_text(file_path):
                    pages_blocks = self.pdf_parser.extract_spatial_blocks(file_path)

                    if pages_blocks:
                        yield {
                            "type": "progress",
                            "step": 3,
                            "message": f"Parsing {sum(len(b) for b in pages_blocks.values())} text blocks...",
                        }
                        for page_num, blocks in pages_blocks.items():
                            rows = self.pattern_matcher.extract_from_blocks(blocks, page_num)
                            for r in rows:
                                r["source"] = "vector"
                            all_rows.extend(rows)

                        logger.info(f"Vector extraction: {len(all_rows)} rows before dedup")

                # --- Phase 2: OCR if not enough from vector extraction ---
                if len(all_rows) < 5:
                    yield {
                        "type": "progress",
                        "step": 2,
                        "message": "Converting PDF to images for OCR...",
                    }
                    try:
                        page_images = self.pdf_parser.convert_to_images(file_path)
                        total = len(page_images)
                        for page_num, img in enumerate(page_images, 1):
                            yield {
                                "type": "progress",
                                "step": 3,
                                "message": f"OCR processing page {page_num}/{total}...",
                            }
                            ocr_result = self.ocr_engine.process_image(img)

                            # Use spatial blocks from OCR if available
                            if ocr_result.get("blocks"):
                                rows = self.pattern_matcher.extract_from_blocks(
                                    ocr_result["blocks"], page_num
                                )
                            else:
                                rows = self.pattern_matcher.extract_from_text(
                                    ocr_result["text"], page_num
                                )
                            for r in rows:
                                r["source"] = "ocr"
                            all_rows.extend(rows)

                    except Exception as e:
                        logger.error(f"OCR failed: {e}")
                        yield {
                            "type": "progress",
                            "step": 3,
                            "message": f"OCR warning: {str(e)[:120]}",
                        }

            elif ext in [".png", ".jpg", ".jpeg"]:
                yield {"type": "progress", "step": 2, "message": "Running OCR on image..."}
                ocr_result = self.ocr_engine.process_image_file(file_path)

                yield {"type": "progress", "step": 3, "message": "Parsing spatial blocks..."}
                if ocr_result.get("blocks"):
                    rows = self.pattern_matcher.extract_from_blocks(ocr_result["blocks"], 1)
                else:
                    rows = self.pattern_matcher.extract_from_text(ocr_result["text"], 1)
                for r in rows:
                    r["source"] = "ocr"
                all_rows.extend(rows)

            else:
                yield {"type": "error", "message": f"Unsupported file format: {ext}"}
                return

            # Deduplicate
            all_rows = self._deduplicate(all_rows)

            yield {
                "type": "progress",
                "step": 4,
                "message": f"Complete — {len(all_rows)} booths extracted",
            }
            yield {"type": "result", "rows": all_rows, "total": len(all_rows)}

        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            yield {"type": "error", "message": f"Extraction failed: {str(e)}"}

    def _deduplicate(self, rows: list[dict]) -> list[dict]:
        """Remove duplicate rows on (booth_number, exhibitor_name, page)."""
        seen: set = set()
        unique: list[dict] = []
        for row in rows:
            key = (
                str(row.get("booth_number", "")).strip().upper(),
                str(row.get("exhibitor_name", "")).strip().upper(),
                row.get("page", ""),
            )
            if key not in seen:
                seen.add(key)
                unique.append(row)
        return unique
