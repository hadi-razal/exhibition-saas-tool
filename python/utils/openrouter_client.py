import os
import json
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("exhibitiq.openrouter")

# Primary model — Claude Opus for maximum accuracy
DEFAULT_MODEL = "anthropic/claude-opus-4.6"
# Fallback models (free) if the primary fails
FALLBACK_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1:free",
]


class OpenRouterClient:
    """Client for interacting with OpenRouter API with automatic model fallback."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY environment variable not set.")

        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key or "dummy",
        )

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = DEFAULT_MODEL,
    ) -> Optional[Dict[str, Any]]:
        """Generate a JSON response from the LLM with automatic model fallback."""
        if not self.api_key:
            return None

        models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]

        for current_model in models_to_try:
            try:
                logger.info(f"Trying model: {current_model}")
                
                # Some free models don't support response_format, so we embed JSON instructions in the prompt
                enhanced_system = system_prompt + "\n\nIMPORTANT: Your entire response must be a single valid JSON object. No markdown, no explanation, just pure JSON."
                
                response = await self.client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": enhanced_system},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=4096,
                    extra_headers={
                        "HTTP-Referer": "https://exhibitiq.app",
                        "X-Title": "ExhibitIQ Floor Plan Extractor",
                    },
                )

                content = response.choices[0].message.content
                if not content:
                    continue

                content = content.strip()
                # Strip markdown code fences
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                # Try to find JSON object in the response
                # Sometimes models wrap JSON in text
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    content = content[json_start:json_end]

                parsed = json.loads(content)
                logger.info(f"Successfully got response from {current_model}")
                return parsed

            except Exception as e:
                error_str = str(e)
                logger.warning(f"Model {current_model} failed: {error_str[:200]}")
                # If it's a 402 (insufficient credits), try next model
                if "402" in error_str or "insufficient" in error_str.lower():
                    continue
                # For other errors, also try next model
                continue

        logger.error("All models failed for OpenRouter request")
        return None

    async def generate_json_with_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str,
        model: str = DEFAULT_MODEL,
    ) -> Optional[Dict[str, Any]]:
        """Generate a JSON response from a vision-capable LLM using an image input."""
        if not self.api_key:
            return None

        import base64
        from pathlib import Path

        # Read and encode the image
        img_path = Path(image_path)
        if not img_path.exists():
            logger.error(f"Image not found: {image_path}")
            return None

        ext = img_path.suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/png")

        with open(img_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Only vision-capable models
        vision_models = [model, "google/gemini-2.0-flash-exp:free"]

        for current_model in vision_models:
            try:
                logger.info(f"Trying vision model: {current_model}")

                enhanced_system = system_prompt + "\n\nIMPORTANT: Your entire response must be a single valid JSON object. No markdown, no explanation, just pure JSON."

                response = await self.client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": enhanced_system},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{image_data}",
                                    },
                                },
                            ],
                        },
                    ],
                    temperature=0.1,
                    max_tokens=4096,
                    extra_headers={
                        "HTTP-Referer": "https://exhibitiq.app",
                        "X-Title": "ExhibitIQ Floor Plan Extractor",
                    },
                )

                content = response.choices[0].message.content
                if not content:
                    continue

                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    content = content[json_start:json_end]

                parsed = json.loads(content)
                logger.info(f"Vision extraction successful with {current_model}")
                return parsed

            except Exception as e:
                logger.warning(f"Vision model {current_model} failed: {str(e)[:200]}")
                continue

        logger.error("All vision models failed")
        return None

