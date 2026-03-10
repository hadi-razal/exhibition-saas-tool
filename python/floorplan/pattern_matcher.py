"""
Pattern Matcher — Extracts booth data from text blocks.

Key design: works on TEXT BLOCKS (spatial groups) not individual lines.
Each block typically represents one booth's text cluster, so we can
identify booth_number, exhibitor_name, booth_size, area_sqm within a block.
"""
import re
import logging
from typing import Optional

logger = logging.getLogger("exhibitiq.floorplan.pattern_matcher")

# ── Non-exhibitor blocklist ───────────────────────────────────────────────────
NON_EXHIBITOR_TERMS: set[str] = {
    "toilet", "toilets", "restroom", "restrooms", "wc", "bathroom", "bathrooms",
    "men", "women", "mens", "womens", "ladies", "gents", "male", "female",
    "accessible", "disabled",
    "entrance", "main entrance", "side entrance", "entry", "entries",
    "exit", "exits", "emergency exit", "fire exit", "fire escape", "emergency",
    "lobby", "foyer", "corridor", "corridors", "aisle", "aisles",
    "walkway", "walkways", "pathway", "gangway", "passage",
    "reception", "registration", "information", "info", "helpdesk", "help desk",
    "visitor", "visitors", "services",
    "storage", "utility", "technical", "service", "loading",
    "freight", "forklift", "loading bay", "loading dock",
    "electrical", "generator", "hvac", "mechanical",
    "cafeteria", "restaurant", "cafe", "café", "bar", "catering", "food",
    "staff", "staff only", "organizer", "organiser", "office",
    "vip", "media", "press", "media center", "media centre",
    "press center", "press centre", "speaker", "speakers",
    "conference", "seminar", "seminar room", "meeting", "meeting room",
    "theatre", "theater", "auditorium",
    "first aid", "medical", "ambulance", "security", "police",
    "prayer", "prayer room", "smoking", "atm", "banking",
    "cloakroom", "wardrobe", "luggage", "baggage",
    "parking", "car park",
    "lift", "elevator", "escalator", "stairs", "staircase", "stairway",
    "networking", "networking zone", "networking lounge",
    "delegation", "delegation zone", "expert hub",
    "speaker lounge", "speakers lounge", "green room",
    "business center", "business centre",
    "eingang", "ausgang", "toilette", "herren", "damen",
    "sortie", "entree", "entrée",
}

NON_EXHIBITOR_WORDS: set[str] = {
    "entrance", "exit", "toilet", "toilets", "restroom", "wc",
    "men", "women", "ladies", "gents", "lobby", "foyer",
    "corridor", "reception", "registration", "storage", "cafeteria",
    "restaurant", "cafe", "bar", "staff", "organizer", "vip",
    "media", "press", "speaker", "conference", "seminar",
    "theatre", "theater", "security", "police", "stairs",
    "elevator", "lift", "escalator", "loading", "freight",
    "parking", "smoking", "prayer", "networking", "delegation",
}

# ── Patterns ──────────────────────────────────────────────────────────────────

BOOTH_PATTERNS = [
    r"\b([A-Z]{1,3}\d[A-Z]\d{2,3})\b",           # SAJ09, S1A13, SAK07
    r"\b([A-Z]{1,3}[-_]?[A-Z][-_]?\d{2,3})\b",   # AR-E10, AR-F10, S1-A40
    r"\b(\d{1,2}[A-Z]\d{1,3})\b",                 # 6A31, 7A32, 6B30
    r"\b(\d{3,5}[A-Z]?)\b",                       # 4240, 4230, 1234A
    r"\b(ST(?:AND)?[-:\s]\d{1,5})\b",             # STAND 102
    r"\b(BOOTH[-:\s]\d{1,5})\b",                  # BOOTH 42
    r"\b([A-Z]{1,2}[-_]?\d{1,4})\b",              # A12, B-14, C3
]

SIZE_PATTERNS = [
    r"(\d+(?:\.\d+)?\s*[xX×]\s*\d+(?:\.\d+)?)\s*(?:M\b|m\b|meter|metre)?",
    r"(\d+(?:\.\d+)?\s*[xX×]\s*\d+(?:\.\d+)?)",
]

AREA_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*(?:sq\.?\s*m\.?|sqm|m²|m2|square\s*met(?:er|re)s?)\b",
    r"(\d{2,4})\s+sq",
]

HALL_PATTERNS = [
    r"\b(Hall\s*[-:]?\s*\d{1,3}(?:\s*[A-Z])?)\b",
    r"\b(Hall\s+[A-Z][a-zA-Z\s]{2,30})\b",
    r"\b(HALL\s*[-:]?\s*\d{1,3})\b",
    r"\b(Halle\s*[-:]?\s*\d{1,3})\b",
    r"\b(Pavilion\s*[-:]?\s*[\d\w]{1,10})\b",
    r"\b(Pavillon\s*[-:]?\s*[\d\w]{1,10})\b",
]

ZONE_PATTERNS = [
    r"\b(Zone\s*[-:]?\s*[A-Z0-9]{1,5})\b",
    r"\b(Section\s*[-:]?\s*[A-Z0-9]{1,5})\b",
    r"\b(Area\s*[-:]?\s*[A-Z0-9]{1,5})\b",
    r"\b(Block\s*[-:]?\s*[A-Z0-9]{1,5})\b",
    r"\b(Level\s*[-:]?\s*\d{1,2})\b",
]


class PatternMatcher:
    """Extract structured booth data from text blocks produced by OCR or PyMuPDF."""

    def extract_from_blocks(self, blocks: list[str], page_number: int) -> list[dict]:
        """Primary method: process a list of spatial text blocks."""
        rows = []
        for block in blocks:
            block = block.strip()
            if not block or len(block) < 2:
                continue
            row = self._extract_from_block(block, page_number)
            if row:
                rows.append(row)
        return rows

    def extract_from_text(self, text: str, page_number: int) -> list[dict]:
        """Fallback: process plain concatenated text line-by-line."""
        if not text or not text.strip():
            return []
        rows = []
        for line_num, line in enumerate(text.split("\n")):
            line = line.strip()
            if not line or len(line) < 2:
                continue
            row = self._extract_from_line(line, page_number, line_num + 1)
            if row:
                rows.append(row)
        rows.extend(self._extract_tabular(text, page_number))
        return rows

    # ── Block-level ───────────────────────────────────────────────────────────

    def _extract_from_block(self, block: str, page_number: int) -> Optional[dict]:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            return None

        full_text = " ".join(lines)
        row: dict = {"page": page_number}

        booth, booth_line = self._find_booth_in_lines(lines)
        if booth:
            row["booth_number"] = booth

        size, _ = self._match_first(SIZE_PATTERNS, full_text, group=1)
        if size:
            row["booth_size"] = size.strip()

        area, _ = self._match_first(AREA_PATTERNS, full_text, group=1)
        if area:
            row["area_sqm"] = area.strip()

        hall, _ = self._match_first(HALL_PATTERNS, full_text, group=1)
        if hall:
            row["hall"] = hall.strip()

        zone, _ = self._match_first(ZONE_PATTERNS, full_text, group=1)
        if zone:
            row["zone"] = zone.strip()

        name = self._extract_name_from_block(lines, row)
        if name:
            row["exhibitor_name"] = name

        if not row.get("booth_number") and not row.get("exhibitor_name"):
            return None
        if self._is_non_exhibitor_block(row):
            return None

        row["source"] = "block"
        return row

    def _find_booth_in_lines(self, lines: list[str]) -> tuple[Optional[str], int]:
        for pattern in BOOTH_PATTERNS:
            for i, line in enumerate(lines):
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    candidate = m.group(1).strip().upper()
                    if self._is_valid_booth(candidate):
                        return candidate, i
        return None, -1

    def _extract_name_from_block(self, lines: list[str], row: dict) -> Optional[str]:
        name_parts = []
        for line in lines:
            cleaned = self._strip_known_patterns(line)
            if not cleaned or len(cleaned) < 2:
                continue
            if re.fullmatch(r"[\d\s\.\-/]+", cleaned):
                continue
            if self._is_non_exhibitor_string(cleaned):
                continue
            name_parts.append(cleaned)

        if not name_parts:
            return None
        candidate = " ".join(name_parts[:2]).strip()
        if len(candidate) < 2 or not re.search(r"[A-Za-z]", candidate):
            return None
        return candidate[:80]

    # ── Line-level fallback ───────────────────────────────────────────────────

    def _extract_from_line(self, line: str, page_number: int, line_num: int) -> Optional[dict]:
        row: dict = {"page": page_number, "line_number": line_num}
        found = False

        for pattern in BOOTH_PATTERNS:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip().upper()
                if self._is_valid_booth(candidate):
                    row["booth_number"] = candidate
                    found = True
                    break

        size, _ = self._match_first(SIZE_PATTERNS, line, group=1)
        if size:
            row["booth_size"] = size.strip()
            found = True

        area, _ = self._match_first(AREA_PATTERNS, line, group=1)
        if area:
            row["area_sqm"] = area.strip()
            found = True

        hall, _ = self._match_first(HALL_PATTERNS, line, group=1)
        if hall:
            row["hall"] = hall.strip()
            found = True

        zone, _ = self._match_first(ZONE_PATTERNS, line, group=1)
        if zone:
            row["zone"] = zone.strip()
            found = True

        name = self._extract_name_from_line(line)
        if name:
            row["exhibitor_name"] = name
            found = True

        if not found:
            return None
        if self._is_non_exhibitor_block(row):
            return None

        row["source"] = "text"
        row["raw_text"] = line[:200]
        return row

    def _extract_name_from_line(self, line: str) -> Optional[str]:
        cleaned = self._strip_known_patterns(line)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if len(cleaned) < 2 or not re.search(r"[A-Za-z]{2,}", cleaned):
            return None
        if self._is_non_exhibitor_string(cleaned):
            return None
        if len(cleaned) > 80:
            return None
        return cleaned

    def _extract_tabular(self, text: str, page_number: int) -> list[dict]:
        rows = []
        for line in text.split("\n"):
            if "|" not in line and "\t" not in line:
                continue
            cells = [c.strip() for c in re.split(r"[|\t]", line) if c.strip()]
            if len(cells) < 2:
                continue
            row: dict = {"page": page_number, "source": "table"}
            for cell in cells:
                if "booth_number" not in row:
                    for p in BOOTH_PATTERNS:
                        m = re.search(p, cell)
                        if m and self._is_valid_booth(m.group(1)):
                            row["booth_number"] = m.group(1).strip().upper()
                            break
                if "booth_size" not in row:
                    size, _ = self._match_first(SIZE_PATTERNS, cell, group=1)
                    if size:
                        row["booth_size"] = size.strip()
                if "area_sqm" not in row:
                    area, _ = self._match_first(AREA_PATTERNS, cell, group=1)
                    if area:
                        row["area_sqm"] = area.strip()
                if "hall" not in row:
                    hall, _ = self._match_first(HALL_PATTERNS, cell, group=1)
                    if hall:
                        row["hall"] = hall.strip()
            if "booth_number" in row:
                for cell in cells:
                    if "exhibitor_name" in row:
                        break
                    has_booth = any(re.search(p, cell) for p in BOOTH_PATTERNS)
                    has_size = bool(self._match_first(SIZE_PATTERNS, cell, group=1)[0])
                    if not has_booth and not has_size and len(cell) >= 2 and re.search(r"[A-Za-z]{2,}", cell):
                        if not self._is_non_exhibitor_string(cell):
                            row["exhibitor_name"] = cell
                row["raw_text"] = line[:200]
                if not self._is_non_exhibitor_block(row):
                    rows.append(row)
        return rows

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _match_first(self, patterns: list[str], text: str, group: int = 0):
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                try:
                    return m.group(group), m
                except IndexError:
                    return m.group(0), m
        return None, None

    def _strip_known_patterns(self, text: str) -> str:
        cleaned = text
        for pattern in BOOTH_PATTERNS + SIZE_PATTERNS + AREA_PATTERNS + HALL_PATTERNS + ZONE_PATTERNS:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b\d+\b", " ", cleaned)
        cleaned = re.sub(r"[^\w\s\.\-&/']", " ", cleaned)
        cleaned = re.sub(r"\b(m|sqm|sq|booth|stand|hall|zone|area|block|level|m2)\b", " ", cleaned, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", cleaned).strip()

    def _is_valid_booth(self, candidate: str) -> bool:
        if not candidate or len(candidate) < 2 or len(candidate) > 15:
            return False
        if candidate.isdigit() and len(candidate) <= 2:
            return False
        if candidate.upper() in NON_EXHIBITOR_WORDS:
            return False
        if re.fullmatch(r"[A-Z]{1,3}", candidate):
            return False
        return True

    def _is_non_exhibitor_string(self, text: str) -> bool:
        t = text.lower().strip()
        if t in NON_EXHIBITOR_TERMS:
            return True
        for term in NON_EXHIBITOR_TERMS:
            if len(term) > 4 and term in t:
                return True
        words = set(t.split())
        if words and words.issubset(NON_EXHIBITOR_WORDS):
            return True
        return False

    def _is_non_exhibitor_block(self, row: dict) -> bool:
        name = str(row.get("exhibitor_name", "")).strip()
        booth = str(row.get("booth_number", "")).strip()
        if name and self._is_non_exhibitor_string(name):
            return True
        if booth and not name and self._is_non_exhibitor_string(booth):
            return True
        return False
