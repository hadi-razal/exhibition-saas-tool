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
    # Restrooms
    "toilet", "toilets", "restroom", "restrooms", "wc", "bathroom", "bathrooms",
    "men", "women", "mens", "womens", "ladies", "gents", "male", "female",
    "accessible", "disabled",
    # Entrances / Exits
    "entrance", "main entrance", "side entrance", "entry", "entries",
    "exit", "exits", "emergency exit", "fire exit", "fire escape", "emergency",
    # Doors / shutters / gates
    "door", "doors", "shutter", "shutter door", "shutter doors",
    "roller shutter", "gate", "gates", "roller door",
    # Passages
    "lobby", "foyer", "corridor", "corridors", "aisle", "aisles",
    "walkway", "walkways", "pathway", "gangway", "passage", "link",
    # Registration / Info
    "reception", "registration", "information", "info", "helpdesk", "help desk",
    "visitor", "visitors", "services",
    # Infrastructure
    "storage", "utility", "technical", "service", "loading",
    "freight", "forklift", "loading bay", "loading dock",
    "electrical", "generator", "hvac", "mechanical",
    "pacu", "pacu tr", "pngf", "fhr",  # HVAC/mechanical codes seen in floor plans
    "ahu", "riser", "duct", "chiller", "compressor", "transformer",
    "bms", "mdb", "db", "smdb", "panel",
    # Food / Beverage
    "cafeteria", "restaurant", "cafe", "café", "bar", "catering", "food",
    "burger", "sushi", "pizza", "grill", "bistro", "diner", "bakery",
    "coffee", "tea", "juice", "smoothie", "snacks", "canteen",
    "food court", "food hall", "dining", "eatery",
    "cafe nero", "nero", "japengo", "hattam", "costa", "starbucks",
    "circle cafe", "cafe arena", "sushi counter",
    "fuel", "outlet",
    # Staff / Org
    "staff", "staff only", "organizer", "organiser", "office",
    # VIP / Media
    "vip", "media", "press", "media center", "media centre",
    "press center", "press centre", "speaker", "speakers",
    # Event spaces
    "conference", "seminar", "seminar room", "meeting", "meeting room",
    "theatre", "theater", "auditorium", "arena", "stage",
    "conference theatre", "conference theater", "conference room",
    "marketing suite", "suite",
    "catering", "cleaning demo area", "demo area", "demo",
    "hygiene",  # standalone "Hygiene" is not a company
    # Rooms / generic spaces
    "room", "majlis", "ssh majlis", "ssh- link arena link", "ssh- link",
    # Medical / Security
    "first aid", "medical", "ambulance", "security", "police",
    "prayer", "prayer room", "smoking", "atm", "banking",
    # Cloakroom
    "cloakroom", "wardrobe", "luggage", "baggage",
    # Transport
    "parking", "car park",
    "lift", "elevator", "escalator", "stairs", "staircase", "stairway",
    # Networking
    "networking", "networking zone", "networking lounge",
    "delegation", "delegation zone", "expert hub",
    "speaker lounge", "speakers lounge", "green room",
    "business center", "business centre",
    # Signage / Decoration
    "signage", "digital signage", "banner", "branding",
    # Counter / generic
    "counter", "kiosk", "stand", "booth",
    # Building elements
    "column", "pillar", "wall", "ceiling", "floor", "roof",
    "window", "glass", "curtain", "partition", "ramp",
    # Misc infrastructure codes
    "ed", "lx", "tr", "fhr", "king",
    "please", "note", "warning", "caution", "notice",
    # Foreign
    "eingang", "ausgang", "toilette", "herren", "damen",
    "sortie", "entree", "entrée", "pantry", "kitchen", "lounge",
    # Halls
    "hall 1", "hall 2", "hall 3", "hall 4", "hall 5",
    "hall 6", "hall 7", "hall 8", "hall 9", "hall 10",
    # Misc labels
    "h & s appr before usin this", "h & s",
    "to book your contact", "jake nixon",
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
    "pantry", "kitchen", "lounge",
    "burger", "sushi", "pizza", "fuel", "outlet", "room",
    "arena", "counter", "link", "suite", "majlis", "signage",
    "digital", "marketing", "stage", "kiosk", "office",
    "catering", "food", "coffee", "dining", "grill",
    # Infrastructure codes
    "door", "shutter", "gate", "column", "pillar", "wall",
    "pacu", "pngf", "ahu", "riser", "duct", "panel",
    "tr", "ed", "lx", "fhr", "king", "please", "note",
}

# ── Patterns ──────────────────────────────────────────────────────────────────

BOOTH_PATTERNS = [
    # Broadcast/media alphanumeric IDs (most specific first)
    r"\b([A-Z]{1,2}\d[-_][A-Z]\d{2,3})\b",            # S1-D10, S2-F30
    r"\b([A-Z]{2,3}[-_][A-Z]\d{2,3})\b",              # AR-A20, S3-B10
    r"\b([A-WYZ]{1,3}\d[A-WYZ]\d{2,3})\b",            # SAJ09, S1A13
    r"\b([A-WYZ]{1,3}[-_]?[A-WYZ][-_]?\d{2,3})\b",
    r"\b(\d{1,2}[A-WYZ]\d{1,3})\b",                   # 6A31, 7A32
    r"\b(\d{1,2}[-_][A-WYZ])\b",                      # 1-A, 2-B
    r"\b([A-WYZ]\d{1,3})\b",                          # A7, G24, A01, F27
    r"\b(\d{3,5}[A-WYZ]?)\b",                         # 4240, 4230, 1234A (3+ digits)
    r"\b(?:STAND|BOOTH)\s*[-:]?\s*([A-Z0-9\-_]{1,10})\b",  # STAND 102, BOOTH 42
    r"\b([A-WYZ]{1,2}[-_]?\d{1,4})\b",                # A12, B-14
    # NOTE: No standalone short numbers — they are dimensions, not booth numbers!
]

SIZE_PATTERNS = [
    r"(\d+(?:\.\d+)?\s*[xX×]\s*\d+(?:\.\d+)?)\s*(?:M\b|m\b|meter|metre)?",
    r"(\d+(?:\.\d+)?\s*[xX×]\s*\d+(?:\.\d+)?)",
]

AREA_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*m²",                          # 180m², 307.5m² (no space, no word boundary)
    r"(\d+(?:\.\d+)?)\s*sq\.\s*m\.",                   # 207 sq.m. (with dots, energy format)
    r"(\d+(?:\.\d+)?)\s*(?:sq\.?\s*m\.?|sqm|m2|square\s*met(?:er|re)s?)\b",
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

    def extract_vape_show_from_text(self, text: str, page_number: int) -> list[dict]:
        """
        Specialized extractor for Vape Show / trade show style floor plans.

        These floor plans embed booth data as inline text:
          [dim] [dim] [dim] [dim] ExhibitorName [dim?] BoothNumber AreaM2

        Strategy:
        1. Find all BoothNumber+Area patterns (4-5 digit number followed by m²)
        2. Look backward from each match to isolate the exhibitor name
           (the name sits between dimension numbers which are 1-2 digits)
        """
        rows = []
        seen_booths: set = set()

        # Match: 4-5 digit booth number followed by an area in m²
        booth_area_re = re.compile(r"(\d{4,5})\s+(\d+(?:\.\d+)?)\s*m²")

        for m in booth_area_re.finditer(text):
            booth = m.group(1)
            area = m.group(2)

            if not self._is_valid_booth(booth):
                continue
            if booth in seen_booths:
                continue

            # Get up to 200 chars before this match to find the exhibitor name
            start = m.start()
            before = text[max(0, start - 200): start]

            # Strip trailing dimension numbers and whitespace
            before_clean = re.sub(r"[\d.\s]+$", "", before).strip()

            # Split on standalone 1-2 digit numbers (dimensions like 6, 10, 12, 20.5)
            # to isolate name segments
            segments = re.split(r"\b\d{1,2}(?:\.\d+)?\b", before_clean)

            name = ""
            for seg in reversed(segments):
                seg = seg.strip()
                # Remove any leading/trailing numbers or punctuation noise
                seg = re.sub(r"^[\d\s.\-/]+", "", seg).strip()
                seg = re.sub(r"[\d\s.\-/]+$", "", seg).strip()
                if seg and len(seg) >= 2 and re.search(r"[A-Za-z]", seg):
                    if not self._is_non_exhibitor_string(seg):
                        name = seg
                        break

            if not name or len(name) < 2:
                continue

            seen_booths.add(booth)
            rows.append({
                "page": page_number,
                "exhibitor_name": name[:100],
                "booth_number": booth,
                "area_sqm": area,
                "source": "vape_show",
            })

        logger.info(f"Vape show extractor: {len(rows)} booths from page {page_number}")
        return rows

    # ── Block-level ───────────────────────────────────────────────────────────

    def _extract_from_block(self, block: str, page_number: int) -> Optional[dict]:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            return None

        full_text = " ".join(lines)
        row: dict = {"page": page_number}

        booth, booth_line = self._find_booth_in_lines(lines, full_text)
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

        # STRICT: require BOTH booth_number AND exhibitor_name for a valid entry
        if not row.get("booth_number") or not row.get("exhibitor_name"):
            return None
        if self._is_non_exhibitor_block(row):
            return None

        row["source"] = "block"
        return row

    def _find_booth_in_lines(self, lines: list[str], full_text: str = "") -> tuple[Optional[str], int]:
        for pattern in BOOTH_PATTERNS:
            for i, line in enumerate(lines):
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    candidate = m.group(1).strip().upper()
                    if self._is_valid_booth(candidate, full_text):
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
        candidate = " ".join(name_parts).strip()
        if len(candidate) < 2 or not re.search(r"[A-Za-z]", candidate):
            return None
        return candidate[:150]

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

    def _is_valid_booth(self, candidate: str, context: str = "") -> bool:
        if not candidate or len(candidate) < 1 or len(candidate) > 15:
            return False
        if candidate.upper() in NON_EXHIBITOR_WORDS:
            return False
        if re.fullmatch(r"[A-Z]{1,3}", candidate):
            return False
        # Reject pure numbers that are likely dimensions (common floor plan measurements)
        if candidate.isdigit():
            num = int(candidate)
            # Common dimension values in meters: 2-30
            if num <= 30:
                return False
            # Also reject if followed by area unit in context
            if context:
                if re.search(rf"\b{re.escape(candidate)}\s*(?:m²|sq\.?\s*m)", context, re.IGNORECASE):
                    return False
        return True

    def _is_non_exhibitor_string(self, text: str) -> bool:
        t = text.lower().strip()
        if t in NON_EXHIBITOR_TERMS:
            return True
        for term in NON_EXHIBITOR_TERMS:
            if len(term) > 3 and len(term.split()) > 1 and term in t:
                # Multi-word terms match as substring (e.g. "shutter door" in text)
                return True
            elif len(term) > 3 and len(term.split()) == 1:
                # Single-word terms must match as whole word, not substring
                if re.search(r'\b' + re.escape(term) + r'\b', t) and len(t.split()) <= 2:
                    return True
        words = set(t.split())
        if words and words.issubset(NON_EXHIBITOR_WORDS):
            return True
        # Reject text starting with instructional/generic phrases
        JUNK_PREFIXES = (
            "please", "to book", "note:", "note ", "warning", "caution",
            "contact", "email", "call", "visit", "click", "scan",
            "for more", "see ", "refer", "book your", "jake nixon",
            "do not", "don't", "no ", "all rights", "copyright",
            "powered by", "designed by", "floor plan", "floorplan",
        )
        if any(t.startswith(p) for p in JUNK_PREFIXES):
            return True
        # Reject pure measurements like "10m", "6x6", "100 sqm"
        if re.fullmatch(r"[\d\s.xX×m²sqft]+", t):
            return True
        # Reject short names (< 4 chars) that aren't alphanumeric booth-style IDs
        if len(t) < 4 and not re.search(r"\d", t):
            return True
        # Reject repeated text patterns like "SHUTTER DOOR SHUTTER DOOR SHUTTER DOOR"
        # or "PACU TR PACU TR PACU TR"
        words_list = t.split()
        if len(words_list) >= 4:
            # Check if 1-3 word pattern repeats
            for pattern_len in range(1, 4):
                pattern = " ".join(words_list[:pattern_len])
                repeat_count = t.count(pattern)
                if repeat_count >= 3:
                    return True
        # Reject if text contains codes like PNGF-300A9 (infrastructure codes)
        if re.search(r"[A-Z]{2,4}-\d{2,4}[A-Z]\d", text):
            return True
        # Reject entries that are ALL CAPS with only 1-2 chars per word and no digits
        # (like "ED", "LX", "FHR" which are building labels)
        if all(len(w) <= 3 for w in words_list) and len(words_list) <= 2 and not re.search(r"\d", t):
            return True
        return False

    def _is_non_exhibitor_block(self, row: dict) -> bool:
        name = str(row.get("exhibitor_name", "")).strip()
        booth = str(row.get("booth_number", "")).strip()
        if name and self._is_non_exhibitor_string(name):
            return True
        if booth and not name:
            return True  # No name = not valid
        # Reject if the "name" is suspiciously long with repeated patterns
        if name and len(name) > 50:
            words = name.lower().split()
            if len(words) > 4:
                unique_words = set(words)
                if len(unique_words) <= 3:  # Very few unique words = repeated text
                    return True
        return False
