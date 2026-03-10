import json
import logging
from typing import Dict, Any
from utils.openrouter_client import OpenRouterClient

logger = logging.getLogger("exhibitiq.scraper.ai")

class AIScraper:
    def __init__(self):
        self.client = OpenRouterClient()
        self.system_prompt = (
            "You are an expert web data extractor. You are given raw text extracted from an exhibitor's detail profile page. "
            "Your task is to extract comprehensive details about the company."
            "CRITICAL RULES: "
            "1. Output ONLY a valid JSON object. "
            "2. Extract these keys if present: 'email', 'phone', 'website', 'description', 'linkedin', 'twitter', 'facebook', 'country', 'city', 'category', 'booth_number'. "
            "3. If a value is not found, omit the key or return an empty string. "
            "4. Format 'email' as a valid email address."
            "5. Format 'phone' strictly keeping numbers and standard characters like + or -. "
            "6. 'description' should be a concise summary of what the company does (up to 500 characters)."
        )

    async def extract_details(self, text: str) -> Dict[str, Any]:
        """Extract exhibitor details from raw page text using OpenRouter LLM."""
        if not text or len(text.strip()) < 20:
            return {}

        user_prompt = f"Extract exhibitor details from the following profile text:\n\n{text[:15000]}"
        
        try:
            result = await self.client.generate_json(self.system_prompt, user_prompt)
            if result:
                # Sanitize response to ensure string types
                clean_data = {}
                for k, v in result.items():
                    if v and isinstance(v, str):
                        clean_data[k] = v.strip()
                return clean_data
            return {}
        except Exception as e:
            logger.error(f"AI Scraper failed: {e}")
            return {}
