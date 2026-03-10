"""
Floor Plan Classifier — Detects the floor plan type for optimal extraction strategy.

Types detected:
- vape_show  : Trade shows using m² areas, 4-5 digit booth numbers (World Vape Show style)
- broadcast  : Tech/media shows using alphanumeric IDs like S1-D10, AR-A20 (CABSAT style)
- energy     : Energy/petroleum shows using "sq.m." with dots (WPC style)
- general    : Everything else (fallback)
"""
import re
import logging

logger = logging.getLogger("exhibitiq.floorplan.classifier")

TYPE_VAPE_SHOW = "vape_show"
TYPE_BROADCAST = "broadcast"
TYPE_ENERGY = "energy"
TYPE_GENERAL = "general"


class FloorPlanClassifier:
    """Classifies floor plan type from extracted text to guide extraction strategy."""

    def classify(self, text: str) -> str:
        """Return one of the TYPE_* constants based on text content."""
        if not text or len(text.strip()) < 30:
            return TYPE_GENERAL

        sample = text[:10000]

        # Broadcast/Media: alphanumeric IDs like S1-D10, AR-A20, S2-F30
        broadcast_ids = re.findall(r"\b[A-Z]{1,3}\d?[-_][A-Z]\d{2,3}\b", sample)
        if len(broadcast_ids) >= 3:
            return TYPE_BROADCAST

        # Count the different area format indicators
        m2_count = len(re.findall(r"\d+(?:\.\d+)?m²", sample))
        sqm_dot_count = len(re.findall(r"\d+\s*sq\.\s*m\.", sample, re.IGNORECASE))
        sqm_count = len(re.findall(r"\d+\s*(?:sq\.?m\.?|sqm)\b", sample, re.IGNORECASE))

        logger.debug(
            f"Classification — m²:{m2_count} sq.m.:{sqm_dot_count} sqm:{sqm_count} "
            f"broadcast_ids:{len(broadcast_ids)}"
        )

        # Energy exhibitions use "sq.m." notation with dots (like 207 sq.m.)
        if sqm_dot_count >= 3:
            return TYPE_ENERGY

        # Vape show / trade show: uses m² symbol, 4-5 digit booth numbers
        if m2_count >= 3:
            return TYPE_VAPE_SHOW

        # General sq.m. (without dots) → likely energy/large exhibition
        if sqm_count >= 3:
            return TYPE_ENERGY

        return TYPE_GENERAL
