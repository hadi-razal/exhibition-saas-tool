"""
AI Extractor — Uses OpenRouter LLM for intelligent floor plan data extraction.

This is the PRIMARY extraction engine for vector PDFs. It sends raw text blocks
from the PDF to the LLM and receives structured booth data back.
For OCR images, it supplements the pattern matcher to catch missed entries.
"""
import json
import logging
import re
from typing import List, Dict, Any
from utils.openrouter_client import OpenRouterClient

logger = logging.getLogger("exhibitiq.floorplan.ai")


SYSTEM_PROMPT_FLOORPLAN = """You are an expert data extraction assistant specialized in exhibition floor plans.
You are given raw text extracted from an exhibition/trade show floor plan PDF or image.

YOUR TASK: Extract ALL exhibitor booths with their details.

CRITICAL RULES:
1. Output ONLY a valid JSON object: {"booths": [...]}
2. Each booth object MUST have these fields:
   - "booth_number": string (e.g. "3170", "A-12", "5150")
   - "exhibitor_name": string (e.g. "Lami", "VPR Collection", "PGVG Labs")
   - "dimensions": string — the booth width x depth (e.g. "10x6", "4x6", "12x6"). Look for numbers on the edges/borders of each booth cell.
   - "area_sqm": string — the area in square meters if shown (e.g. "60", "120", "24"). Look for values like "60m²", "120m²", "36m²".
3. STRICTLY EXCLUDE non-exhibitor entries:
   - Food outlets, cafes, restaurants
   - Facilities: toilet, entrance, exit, lobby, corridor, room
   - Infrastructure: elevator, stairs, parking, storage
   - Event spaces: conference, meeting room, theatre, lounge, arena, stage
   - Signage, banners, walkways
   - Generic labels: hall names, zone labels
4. Include ALL real company/brand names — even short ones like "Posh", "KIWI", "Myle", "Smiss".
5. For dimensions: Look at the width/depth numbers on booth edges. If a booth shows "10" on one side and "6" on another, the dimensions are "10x6".
6. Normalize booth numbers to uppercase.
7. If there are NO valid exhibitors, return {"booths": []}."""


SYSTEM_PROMPT_VISION = """You are an expert data extraction assistant specialized in exhibition floor plans.
You are looking at a floor plan image from an exhibition/trade show.

YOUR TASK: Extract ALL exhibitor booths visible in the image.

CRITICAL RULES:
1. Output ONLY a valid JSON object: {"booths": [...]}
2. Each booth object MUST have these fields:
   - "booth_number": string — the number shown in or near each booth (usually in the top-left corner)
   - "exhibitor_name": string — the company/brand name shown inside the booth
   - "dimensions": string — width x depth in meters from the numbers on booth edges (e.g. "10x6")
   - "area_sqm": string — area if shown (look for values like "60m²", "120m²")
3. EXCLUDE non-exhibitor items: cafes, toilets, entrances, corridors, signage, walkways, generic labels.
4. Include ALL real company/brand names visible — even short names.
5. Read the numbers on the edges of each booth cell to determine dimensions.
6. If there are NO valid exhibitors, return {"booths": []}."""


class AIExtractor:
    def __init__(self):
        self.client = OpenRouterClient()

    def _parse_booth(self, b: dict, source: str = "ai", page: int = None) -> dict | None:
        """Parse a single booth entry from AI response with field name flexibility."""
        # Try multiple possible field names the AI might use
        booth_num = str(
            b.get("booth_number", "") or b.get("number", "") or b.get("booth", "") or b.get("stand", "")
        ).strip().upper()

        name = str(
            b.get("exhibitor_name", "") or b.get("company_name", "") or b.get("name", "") or b.get("company", "") or b.get("exhibitor", "")
        ).strip()

        if not booth_num or not name or len(name) < 2:
            return None
        if self._looks_like_facility(name):
            return None

        row = {
            "booth_number": booth_num,
            "exhibitor_name": name,
            "source": source,
        }

        # Dimensions — try multiple field names
        dims = str(
            b.get("dimensions", "") or b.get("dimension", "") or b.get("size", "") or b.get("booth_size", "")
        ).strip()
        if dims and dims.lower() not in ("none", "null", "n/a", ""):
            row["booth_size"] = dims

        # Area — try multiple field names
        area = str(
            b.get("area_sqm", "") or b.get("area", "") or b.get("sqm", "") or b.get("square_meters", "")
        ).strip().replace("m²", "").replace("sqm", "").strip()
        if area and area.lower() not in ("none", "null", "n/a", ""):
            row["area_sqm"] = area

        if page is not None:
            row["page"] = page

        return row

    async def extract_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract booth data directly from a floor plan IMAGE using vision AI.
        This bypasses Tesseract entirely — the LLM reads the image directly.
        """
        user_prompt = (
            "Look at this exhibition/trade show floor plan image carefully. "
            "Extract EVERY exhibitor booth you can see. For each booth, get:\n"
            "1. The booth number (usually in top-left corner of each cell)\n"
            "2. The company/brand name (shown inside the cell)\n"
            "3. The dimensions in meters (numbers on the edges, e.g. width x depth like '10x6')\n"
            "4. The area in sqm if shown (look for values like '60m²')\n\n"
            "Be thorough — extract ALL booths visible in the image."
        )

        try:
            result = await self.client.generate_json_with_image(
                SYSTEM_PROMPT_VISION, user_prompt, image_path
            )
            if result and "booths" in result:
                valid = []
                for b in result["booths"]:
                    row = self._parse_booth(b, source="ai_vision")
                    if row:
                        valid.append(row)

                logger.info(f"AI vision extracted {len(valid)} booths from image")
                return valid

        except Exception as e:
            logger.error(f"AI vision extraction failed: {e}")

        return []

    async def extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract booth data from raw text using OpenRouter LLM."""
        if not text or len(text.strip()) < 10:
            return []

        chunks = self._chunk_text(text, max_chars=12000)
        all_booths = []

        for chunk in chunks:
            user_prompt = (
                "Extract ALL exhibitor booths from this floor plan text. "
                "For each booth get: booth_number, exhibitor_name, dimensions (WxD), and area_sqm.\n\n"
                f"{chunk}"
            )

            try:
                result = await self.client.generate_json(SYSTEM_PROMPT_FLOORPLAN, user_prompt)
                if result and "booths" in result:
                    for b in result["booths"]:
                        row = self._parse_booth(b, source="ai")
                        if row:
                            all_booths.append(row)

            except Exception as e:
                logger.error(f"AI Extraction chunk failed: {e}")
                continue

        logger.info(f"AI extracted {len(all_booths)} valid booths")
        return all_booths

    async def extract_from_blocks(self, blocks: List[str], page_number: int) -> List[Dict[str, Any]]:
        """
        Extract from spatial blocks — used as PRIMARY extraction for vector PDFs.
        Sends all blocks as a single prompt for maximum context.
        """
        if not blocks:
            return []

        formatted = "\n---BLOCK---\n".join(blocks)
        user_prompt = (
            "Below are text blocks from an exhibition floor plan PDF. "
            "Each block (separated by ---BLOCK---) is text from one spatial region. "
            "Extract ALL exhibitor booths. For each get: booth_number, exhibitor_name, dimensions (WxD), area_sqm.\n\n"
            f"{formatted[:15000]}"
        )

        try:
            result = await self.client.generate_json(SYSTEM_PROMPT_FLOORPLAN, user_prompt)
            if result and "booths" in result:
                valid = []
                for b in result["booths"]:
                    row = self._parse_booth(b, source="ai", page=page_number)
                    if row:
                        valid.append(row)

                logger.info(f"AI block extraction: {len(valid)} booths from page {page_number}")
                return valid

        except Exception as e:
            logger.error(f"AI block extraction failed: {e}")

        return []

    def _chunk_text(self, text: str, max_chars: int = 12000) -> List[str]:
        """Split text into chunks that fit within the model's context."""
        if len(text) <= max_chars:
            return [text]

        chunks = []
        lines = text.split("\n")
        current_chunk = []
        current_len = 0

        for line in lines:
            line_len = len(line) + 1
            if current_len + line_len > max_chars and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_len = 0
            current_chunk.append(line)
            current_len += line_len

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _looks_like_facility(self, name: str) -> bool:
        """Post-validation check to reject facility-looking names."""
        t = name.lower().strip()
        facility_terms = {
            "cafe", "café", "restaurant", "burger", "sushi", "pizza", "food",
            "catering", "kitchen", "pantry", "coffee", "nero", "japengo",
            "costa", "starbucks", "hattam", "fuel", "outlet", "bar",
            "toilet", "restroom", "entrance", "exit", "lobby", "foyer",
            "corridor", "room", "reception", "registration", "storage",
            "elevator", "lift", "stairs", "escalator", "parking",
            "conference", "seminar", "meeting", "theatre", "theater",
            "auditorium", "lounge", "arena", "marketing suite", "majlis",
            "signage", "digital signage", "banner", "branding", "link",
            "walkway", "passage", "counter", "circle cafe", "cafe arena",
            "cafe nero", "sushi counter", "ssh majlis", "ssh- link",
            "main entrance", "side entrance", "fire exit",
        }
        if t in facility_terms:
            return True
        for term in facility_terms:
            if len(term) > 3 and term in t:
                return True
        if re.fullmatch(r"[\d\s.xX×m²]+", t):
            return True
        return False
