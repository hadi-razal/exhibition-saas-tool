"""
PDF Parser — Direct text extraction and page-to-image conversion.

Key improvement: PyMuPDF spatial block extraction with BOOTH CELL MERGING.
For vector PDFs, PyMuPDF extracts text with bounding boxes. We merge
nearby text elements into "booth cells" so booth numbers and exhibitor
names that belong together are grouped into a single block.
"""
import logging
import re
from typing import List, Tuple

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

        Uses word-level extraction with bounding boxes, then clusters nearby
        words into booth cells using spatial proximity. This ensures booth
        numbers, exhibitor names, and dimensions within the same cell are
        grouped together.

        Returns: {page_num: [block_text, block_text, ...]}
        """
        pages_blocks: dict[int, list[str]] = {}

        try:
            import fitz

            doc = fitz.open(file_path)
            has_content = False

            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1

                # Use word-level extraction for precise positioning
                # Each word: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
                words = page.get_text("words")
                if not words:
                    continue

                # Also get blocks for fallback
                raw_blocks = page.get_text("blocks")

                # Try clustering words into booth cells
                booth_cells = self._cluster_into_cells(words, page)
                
                if booth_cells and len(booth_cells) > 5:
                    pages_blocks[page_num] = booth_cells
                    has_content = True
                    logger.info(f"Page {page_num}: clustered {len(words)} words into {len(booth_cells)} booth cells")
                else:
                    # Fallback to standard blocks
                    text_blocks = []
                    for blk in raw_blocks:
                        block_type = blk[6] if len(blk) > 6 else 0
                        if block_type != 0:
                            continue
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

    def _cluster_into_cells(self, words: list, page) -> List[str]:
        """
        Cluster words into booth cells based on spatial proximity.
        
        Strategy: Use PyMuPDF's block grouping as primary clustering, then
        merge blocks that overlap vertically and are within close horizontal
        distance (likely same booth cell).
        """
        if not words:
            return []

        # Step 1: Group words by their block_no (PyMuPDF's native grouping)
        block_groups: dict[int, list] = {}
        for w in words:
            block_no = w[5]
            if block_no not in block_groups:
                block_groups[block_no] = []
            block_groups[block_no].append(w)

        # Step 2: For each block group, compute bounding box and text
        blocks_with_bbox = []
        for block_no, group_words in block_groups.items():
            x0 = min(w[0] for w in group_words)
            y0 = min(w[1] for w in group_words)
            x1 = max(w[2] for w in group_words)
            y1 = max(w[3] for w in group_words)
            
            # Sort words by line (y) then position (x)
            sorted_words = sorted(group_words, key=lambda w: (round(w[1] / 3), w[0]))
            
            # Build text from words, grouping by line
            lines = {}
            for w in sorted_words:
                line_key = round(w[1] / 3)  # Group words within ~3 pts vertically
                if line_key not in lines:
                    lines[line_key] = []
                lines[line_key].append(w[4])
            
            text = "\n".join(" ".join(words_in_line) for words_in_line in lines.values())
            
            if text.strip():
                blocks_with_bbox.append({
                    "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                    "text": text.strip(),
                    "block_no": block_no
                })

        # Step 3: Merge nearby blocks that likely belong to the same booth
        # Use a tolerance based on typical booth cell sizes
        page_width = page.rect.width
        page_height = page.rect.height
        
        # Estimate cell size from block density
        if len(blocks_with_bbox) > 10:
            # Typical floor plan has many small cells
            merge_tolerance_x = page_width * 0.02  # 2% of page width
            merge_tolerance_y = page_height * 0.01  # 1% of page height
        else:
            merge_tolerance_x = page_width * 0.05
            merge_tolerance_y = page_height * 0.03

        merged = self._merge_nearby_blocks(blocks_with_bbox, merge_tolerance_x, merge_tolerance_y)
        
        return [b["text"] for b in merged if b["text"].strip()]

    def _merge_nearby_blocks(self, blocks: list, tol_x: float, tol_y: float) -> list:
        """
        Merge blocks that are very close together (same booth cell).
        Two blocks merge if their bounding boxes overlap or are within tolerance.
        """
        if not blocks:
            return []

        # Sort by position (top-left to bottom-right)
        blocks = sorted(blocks, key=lambda b: (b["y0"], b["x0"]))
        
        merged = list(blocks)
        changed = True
        max_iterations = 5  # prevent infinite loops
        
        while changed and max_iterations > 0:
            changed = False
            max_iterations -= 1
            new_merged = []
            used = set()
            
            for i in range(len(merged)):
                if i in used:
                    continue
                    
                current = dict(merged[i])
                
                for j in range(i + 1, len(merged)):
                    if j in used:
                        continue
                    
                    other = merged[j]
                    
                    # Check if blocks are nearby
                    x_overlap = (current["x0"] - tol_x <= other["x1"] and 
                                current["x1"] + tol_x >= other["x0"])
                    y_overlap = (current["y0"] - tol_y <= other["y1"] and 
                                current["y1"] + tol_y >= other["y0"])
                    
                    if x_overlap and y_overlap:
                        # Merge: expand bounding box and combine text
                        current["x0"] = min(current["x0"], other["x0"])
                        current["y0"] = min(current["y0"], other["y0"])
                        current["x1"] = max(current["x1"], other["x1"])
                        current["y1"] = max(current["y1"], other["y1"])
                        current["text"] = current["text"] + "\n" + other["text"]
                        used.add(j)
                        changed = True
                
                new_merged.append(current)
            
            merged = new_merged
        
        return merged

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
