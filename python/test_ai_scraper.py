import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.ai_scraper import AIScraper

async def main():
    profile_text = """
    About Apple Inc:
    Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
    We are located at Booth SAJ17 in Hall 3.
    Reach out to us via email at hello@apple.com or call us at +1-800-692-7753.
    Follow us on Twitter: https://twitter.com/apple
    Website: www.apple.com
    Country: United States
    City: Cupertino
    Category: Electronics & Technology
    """
    
    scraper = AIScraper()
    print("Sending request to OpenRouter...")
    result = await scraper.extract_details(profile_text)
    
    print("\n--- Extracted Data ---")
    for k, v in result.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    asyncio.run(main())
