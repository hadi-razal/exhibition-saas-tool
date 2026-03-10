"""
Floor Plan Extractor — Main orchestrator.

Extraction pipeline:
1. For vector PDFs  → PyMuPDF spatial block extraction → AI-first parsing via OpenRouter
2. For image PDFs   → pdf2image + OCR → AI parsing + pattern matcher fallback
3. For image files  → AI Vision (direct) → OCR fallback → pattern matcher fallback
4. For ALL PDFs     → AI Vision on converted images as secondary attempt

AI extraction is the PRIMARY engine. Pattern matching is the fallback when AI is unavailable.
"""
import logging
import tempfile
import os
from pathlib import Path
from typing import AsyncGenerator

from .pdf_parser import PDFParser
from .ocr_engine import OCREngine
from .pattern_matcher import PatternMatcher
from .floor_plan_classifier import FloorPlanClassifier, TYPE_VAPE_SHOW
from .ai_extractor import AIExtractor

logger = logging.getLogger("exhibitiq.floorplan")


class FloorPlanExtractor:
    """Orchestrates the floor plan data extraction pipeline."""

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.ocr_engine = OCREngine()
        self.pattern_matcher = PatternMatcher()
        self.classifier = FloorPlanClassifier()
        self.ai_extractor = AIExtractor()

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

                plan_type = TYPE_VAPE_SHOW
                pages_text: dict[int, str] = {}

                if self.pdf_parser.has_embedded_text(file_path):
                    pages_blocks = self.pdf_parser.extract_spatial_blocks(file_path)

                    if pages_blocks:
                        combined = "\n".join(
                            "\n".join(blocks) for blocks in pages_blocks.values()
                        )
                        plan_type = self.classifier.classify(combined)
                        yield {
                            "type": "progress",
                            "step": 3,
                            "message": f"Detected layout type: {plan_type} — sending to AI for intelligent extraction...",
                        }

                        # AI-FIRST: Send blocks to AI for intelligent extraction
                        for page_num, blocks in pages_blocks.items():
                            yield {
                                "type": "progress",
                                "step": 3,
                                "message": f"AI analyzing page {page_num} blocks...",
                            }
                            ai_rows = await self.ai_extractor.extract_from_blocks(blocks, page_num)
                            if ai_rows:
                                all_rows.extend(ai_rows)
                                logger.info(f"AI extracted {len(ai_rows)} booths from page {page_num}")
                            else:
                                # AI failed — fallback to pattern matcher
                                logger.info(f"AI unavailable for page {page_num}, using pattern matcher")
                                rows = self.pattern_matcher.extract_from_blocks(blocks, page_num)
                                for r in rows:
                                    r["source"] = "vector"
                                all_rows.extend(rows)

                            pages_text[page_num] = "\n".join(blocks)

                        # Also try Vape Show specialized extractor
                        if plan_type == TYPE_VAPE_SHOW and not all_rows:
                            yield {
                                "type": "progress",
                                "step": 3,
                                "message": "Running trade-show pattern extractor...",
                            }
                            for page_num, text in pages_text.items():
                                rows = self.pattern_matcher.extract_vape_show_from_text(text, page_num)
                                all_rows.extend(rows)

                # --- Phase 2: AI Vision on PDF as image (powerful secondary attempt) ---
                # If we got very few results, try converting PDF to image and using vision AI
                if len(all_rows) < 10:
                    yield {
                        "type": "progress",
                        "step": 3,
                        "message": "Trying AI Vision on PDF as image for better extraction...",
                    }
                    try:
                        page_images = self.pdf_parser.convert_to_images(file_path, dpi=200)
                        for page_num, img in enumerate(page_images, 1):
                            # Save temp image for AI vision
                            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                                img.save(tmp, format="PNG")
                                tmp_path = tmp.name
                            try:
                                yield {
                                    "type": "progress",
                                    "step": 3,
                                    "message": f"AI Vision analyzing page {page_num} image...",
                                }
                                vision_rows = await self.ai_extractor.extract_from_image(tmp_path)
                                if vision_rows:
                                    for r in vision_rows:
                                        r["page"] = page_num
                                    # Merge with existing rows
                                    existing_booths = {
                                        (str(r.get("booth_number", "")).upper(), str(r.get("exhibitor_name", "")).upper())
                                        for r in all_rows
                                        if r.get("page") == page_num
                                    }
                                    new_count = 0
                                    for r in vision_rows:
                                        key = (str(r.get("booth_number", "")).upper(), str(r.get("exhibitor_name", "")).upper())
                                        if key not in existing_booths:
                                            all_rows.append(r)
                                            existing_booths.add(key)
                                            new_count += 1
                                    if new_count:
                                        logger.info(f"AI Vision added {new_count} new booths from page {page_num}")
                            finally:
                                os.unlink(tmp_path)
                    except Exception as e:
                        logger.warning(f"AI Vision on PDF failed: {e}")

                # --- Phase 3: OCR if still not enough ---
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

                            ocr_text = ocr_result.get("text", "")
                            if not plan_type or plan_type == TYPE_VAPE_SHOW:
                                plan_type = self.classifier.classify(ocr_text)

                            # AI-first on OCR text too
                            if ocr_text:
                                yield {
                                    "type": "progress",
                                    "step": 3,
                                    "message": f"AI analyzing OCR text from page {page_num}...",
                                }
                                ai_rows = await self.ai_extractor.extract_from_text(ocr_text)
                                if ai_rows:
                                    for r in ai_rows:
                                        r["page"] = page_num
                                    all_rows.extend(ai_rows)
                                else:
                                    # Fallback to pattern matcher
                                    if ocr_result.get("blocks"):
                                        rows = self.pattern_matcher.extract_from_blocks(
                                            ocr_result["blocks"], page_num
                                        )
                                    else:
                                        rows = self.pattern_matcher.extract_from_text(
                                            ocr_text, page_num
                                        )
                                    for r in rows:
                                        r["source"] = "ocr"
                                    all_rows.extend(rows)

                                    if plan_type == TYPE_VAPE_SHOW:
                                        rows = self.pattern_matcher.extract_vape_show_from_text(
                                            ocr_text, page_num
                                        )
                                        all_rows.extend(rows)

                    except Exception as e:
                        logger.error(f"OCR failed: {e}")
                        yield {
                            "type": "progress",
                            "step": 3,
                            "message": f"OCR warning: {str(e)[:200]}",
                        }

            elif ext in [".png", ".jpg", ".jpeg"]:
                yield {"type": "progress", "step": 2, "message": "Analyzing floor plan image with AI vision..."}

                # AI-FIRST: Send image directly to vision model (no Tesseract needed)
                ai_rows = await self.ai_extractor.extract_from_image(file_path)
                if ai_rows:
                    for r in ai_rows:
                        r["page"] = 1
                    all_rows.extend(ai_rows)
                    yield {
                        "type": "progress",
                        "step": 3,
                        "message": f"AI vision found {len(ai_rows)} exhibitors",
                    }
                else:
                    # Fallback: try OCR if AI vision failed
                    yield {"type": "progress", "step": 2, "message": "AI vision unavailable, trying OCR..."}
                    try:
                        ocr_result = self.ocr_engine.process_image_file(file_path)
                        ocr_text = ocr_result.get("text", "")
                        plan_type = self.classifier.classify(ocr_text)

                        # Try AI on OCR text
                        if ocr_text:
                            ai_text_rows = await self.ai_extractor.extract_from_text(ocr_text)
                            if ai_text_rows:
                                for r in ai_text_rows:
                                    r["page"] = 1
                                all_rows.extend(ai_text_rows)
                            else:
                                # Last resort: pattern matcher
                                if ocr_result.get("blocks"):
                                    rows = self.pattern_matcher.extract_from_blocks(ocr_result["blocks"], 1)
                                else:
                                    rows = self.pattern_matcher.extract_from_text(ocr_text, 1)
                                for r in rows:
                                    r["source"] = "ocr"
                                all_rows.extend(rows)

                                if plan_type == TYPE_VAPE_SHOW and ocr_text:
                                    rows = self.pattern_matcher.extract_vape_show_from_text(ocr_text, 1)
                                    all_rows.extend(rows)

                    except RuntimeError as e:
                        logger.warning(f"OCR also failed: {e}")
                        yield {"type": "progress", "step": 3, "message": f"Note: {str(e)[:150]}"}

            else:
                yield {"type": "error", "message": f"Unsupported file format: {ext}"}
                return

            # Post-process: validate and clean all rows
            all_rows = self._validate_rows(all_rows)

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

    def _validate_rows(self, rows: list[dict]) -> list[dict]:
        """
        Post-process validation: remove junk entries that slipped through.
        """
        import re
        valid = []
        for row in rows:
            booth = str(row.get("booth_number", "")).strip()
            name = str(row.get("exhibitor_name", "")).strip()
            
            # Must have at least a booth number OR a name
            if not booth and not name:
                continue
                
            # Reject entries where booth_number is a pure small number (dimension)
            if booth and booth.isdigit() and int(booth) <= 30:
                # Unless it has a valid company name — in which case, keep the name
                if name and len(name) >= 4:
                    row["booth_number"] = ""  # Clear the bad booth number, keep the name
                else:
                    continue
            
            # Reject entries where the name is just "AS", "BCC" style abbreviations
            # only if they have no other data
            if name and len(name) <= 2 and not booth:
                continue
            
            # Reject entries where name looks like "Conference Theatre", "Catering"
            name_lower = name.lower()
            junk_names = {
                "conference theatre", "conference theater", "catering",
                "conference", "theatre", "theater", "hygiene",
                "cleaning demo area", "demo area",
            }
            if name_lower in junk_names:
                continue
            if any(name_lower.startswith(p) for p in ("conference ", "catering ")):
                continue
            
            valid.append(row)
        
        return valid

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
