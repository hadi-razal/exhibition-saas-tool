"""
Pattern Matcher — Regex-based extraction of booth numbers, sizes, halls, and exhibitor names.
"""
import re
import logging
from typing import Optional

logger = logging.getLogger("exhibitiq.floorplan.pattern_matcher")


class PatternMatcher:
    """Extract structured booth data from raw text using regex and heuristics."""

    # Booth number patterns: A12, B-14, C21, H5-B13, ST-102, etc.
    BOOTH_PATTERNS = [
        r"\b([A-Z]{1,3}[-\s]?\d{1,5}(?:[-/][A-Z]?\d{0,4})?)\b",  # A12, B-14, H5-B13
        r"\b(ST[-\s]?\d{2,5})\b",  # ST-102
        r"\b(STAND\s*[-:]?\s*\d{1,5})\b",  # STAND 102, STAND: 102
        r"\b(BOOTH\s*[-:]?\s*\d{1,5})\b",  # BOOTH 42
        r"\b(\d{1,2}[A-Z]\d{1,4})\b",  # 5A123
    ]

    # Size patterns: 3x3, 3 x 4, 12 sqm, 24 m2, 18 sq.m, etc.
    SIZE_PATTERNS = [
        r"\b(\d+(?:\.\d+)?\s*[xX×]\s*\d+(?:\.\d+)?)\s*(?:m|meter|metre)?",  # 3x3, 3 x 4
        r"\b(\d+(?:\.\d+)?)\s*(?:sqm|sq\.?\s*m|m²|m2|square\s*met(?:er|re)s?)\b",  # 12 sqm, 24 m2
        r"\b(\d+(?:\.\d+)?)\s*(?:sq\.?\s*ft|ft²|ft2|square\s*feet)\b",  # 200 sq ft
    ]

    # Hall patterns: Hall 1, Hall 5, Sheikh Saeed Hall, etc.
    HALL_PATTERNS = [
        r"\b(Hall\s*[-:]?\s*\d{1,3}(?:\s*[A-Z])?)\b",  # Hall 1, Hall 5A
        r"\b(Hall\s+[A-Z][a-zA-Z\s]{2,30})\b",  # Hall Sheikh Saeed
        r"\b(HALL\s*[-:]?\s*\d{1,3})\b",  # HALL 1
        r"\b(Halle\s*[-:]?\s*\d{1,3})\b",  # Halle 1 (German)
        r"\b(Pavilion\s*[-:]?\s*\d{1,3})\b",  # Pavilion 1
    ]

    # Zone/Section patterns
    ZONE_PATTERNS = [
        r"\b(Zone\s*[-:]?\s*[A-Z0-9]{1,5})\b",
        r"\b(Section\s*[-:]?\s*[A-Z0-9]{1,5})\b",
        r"\b(Area\s*[-:]?\s*[A-Z0-9]{1,5})\b",
        r"\b(Block\s*[-:]?\s*[A-Z0-9]{1,5})\b",
        r"\b(Level\s*[-:]?\s*\d{1,2})\b",
    ]

    def extract_from_text(self, text: str, page_number: int = 1) -> list[dict]:
        """
        Extract structured rows from raw text.
        Uses line-by-line analysis and cross-line grouping.
        """
        if not text or not text.strip():
            return []

        rows = []
        lines = text.split("\n")

        # First pass: extract data from each line
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 2:
                continue

            row = self._extract_from_line(line, page_number)
            if row and (row.get("booth_number") or row.get("exhibitor_name")):
                row["line_number"] = line_num + 1
                rows.append(row)

        # Second pass: try to find tabular data (pipe/tab separated)
        table_rows = self._extract_tabular(text, page_number)
        rows.extend(table_rows)

        # Third pass: extract any remaining booth numbers not yet captured
        all_found_booths = {r.get("booth_number") for r in rows if r.get("booth_number")}
        additional = self._extract_standalone_booths(text, page_number, all_found_booths)
        rows.extend(additional)

        logger.info(f"Page {page_number}: extracted {len(rows)} rows")
        return rows

    def _extract_from_line(self, line: str, page_number: int) -> Optional[dict]:
        """Extract structured data from a single line of text."""
        row = {"page": page_number}
        found_something = False

        # Extract booth number
        for pattern in self.BOOTH_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                booth = match.group(1).strip().upper()
                # Validate: not just a number, not too long
                if len(booth) <= 15 and not booth.isdigit():
                    row["booth_number"] = booth
                    found_something = True
                    break

        # Extract size
        for pattern in self.SIZE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                row["booth_size"] = match.group(0).strip()
                found_something = True
                break

        # Extract hall
        for pattern in self.HALL_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                row["hall"] = match.group(1).strip()
                found_something = True
                break

        # Extract zone
        for pattern in self.ZONE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                row["zone"] = match.group(1).strip()
                found_something = True
                break

        # Try to extract exhibitor name
        # Heuristic: text near a booth number that looks like a company name
        name = self._extract_exhibitor_name(line, row.get("booth_number"))
        if name:
            row["exhibitor_name"] = name
            found_something = True

        # Keep raw text for reference
        if found_something:
            row["raw_text"] = line[:200]

        return row if found_something else None

    def _extract_exhibitor_name(
        self, line: str, booth_number: Optional[str]
    ) -> Optional[str]:
        """
        Try to extract a company/exhibitor name from a line.
        Heuristic: multi-word text that isn't a booth code or size.
        """
        # Remove booth numbers, sizes, halls from the line
        cleaned = line
        for pattern in self.BOOTH_PATTERNS + self.SIZE_PATTERNS + self.HALL_PATTERNS + self.ZONE_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Remove common noise words
        noise = [
            r"\b(booth|stand|hall|zone|section|area|block|level|sqm|m2|sq\.m)\b",
            r"[-|/\\:;,]",
            r"\b\d+\b",
        ]
        for n in noise:
            cleaned = re.sub(n, " ", cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Check if remaining text looks like a name (2+ chars, has letters)
        if len(cleaned) >= 3 and re.search(r"[a-zA-Z]{2,}", cleaned):
            # Limit length
            if len(cleaned) <= 100:
                return cleaned.title()

        return None

    def _extract_tabular(self, text: str, page_number: int) -> list[dict]:
        """Extract data from pipe/tab separated tabular format."""
        rows = []
        lines = text.split("\n")

        for line in lines:
            if "|" in line or "\t" in line:
                cells = re.split(r"[|\t]", line)
                cells = [c.strip() for c in cells if c.strip()]

                if len(cells) >= 2:
                    row = {"page": page_number, "source": "table"}

                    for cell in cells:
                        # Try to identify cell content
                        for pattern in self.BOOTH_PATTERNS:
                            if re.search(pattern, cell) and "booth_number" not in row:
                                match = re.search(pattern, cell)
                                if match:
                                    row["booth_number"] = match.group(1).strip().upper()

                        for pattern in self.SIZE_PATTERNS:
                            if re.search(pattern, cell, re.IGNORECASE) and "booth_size" not in row:
                                row["booth_size"] = cell.strip()

                        for pattern in self.HALL_PATTERNS:
                            if re.search(pattern, cell, re.IGNORECASE) and "hall" not in row:
                                match = re.search(pattern, cell, re.IGNORECASE)
                                if match:
                                    row["hall"] = match.group(1).strip()

                    # Remaining cells might be exhibitor names
                    if "booth_number" in row:
                        for cell in cells:
                            is_booth = any(re.search(p, cell) for p in self.BOOTH_PATTERNS)
                            is_size = any(
                                re.search(p, cell, re.IGNORECASE) for p in self.SIZE_PATTERNS
                            )
                            is_hall = any(
                                re.search(p, cell, re.IGNORECASE) for p in self.HALL_PATTERNS
                            )
                            if (
                                not is_booth
                                and not is_size
                                and not is_hall
                                and len(cell) >= 3
                                and re.search(r"[a-zA-Z]{2,}", cell)
                                and "exhibitor_name" not in row
                            ):
                                row["exhibitor_name"] = cell.strip()

                        row["raw_text"] = line[:200]
                        rows.append(row)

        return rows

    def _extract_standalone_booths(
        self, text: str, page_number: int, already_found: set
    ) -> list[dict]:
        """Find booth numbers in the text that weren't captured in line-by-line pass."""
        rows = []
        for pattern in self.BOOTH_PATTERNS[:2]:  # Use primary patterns only
            for match in re.finditer(pattern, text):
                booth = match.group(1).strip().upper()
                if booth not in already_found and len(booth) <= 15 and not booth.isdigit():
                    rows.append({
                        "page": page_number,
                        "booth_number": booth,
                        "source": "standalone",
                    })
                    already_found.add(booth)

        return rows
