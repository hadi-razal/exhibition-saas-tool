import sys
import asyncio
from pathlib import Path

# Add project root to pythonpath
sys.path.append(r"c:\Users\hadhi\Desktop\Personal\Programming\exhibition-saas-tool\python")

from floorplan.extractor import FloorPlanExtractor

async def main():
    images = [
        r"C:\Users\hadhi\.gemini\antigravity\brain\575a7455-a3f0-4e45-a0b1-08bd4f90e3e2\media__1773155262082.png",
        r"C:\Users\hadhi\.gemini\antigravity\brain\575a7455-a3f0-4e45-a0b1-08bd4f90e3e2\media__1773155265352.png",
        r"C:\Users\hadhi\.gemini\antigravity\brain\575a7455-a3f0-4e45-a0b1-08bd4f90e3e2\media__1773155269811.png",
        r"C:\Users\hadhi\.gemini\antigravity\brain\575a7455-a3f0-4e45-a0b1-08bd4f90e3e2\media__1773155272328.png",
    ]
    
    extractor = FloorPlanExtractor()
    for img in images:
        if not Path(img).exists():
            continue
        print(f"\n{'='*50}\nTesting {Path(img).name}\n{'='*50}")
        try:
            async for event in extractor.extract(img):
                if event["type"] == "result":
                    print(f"Extracted {event['total']} booths.")
                    print("-" * 30)
                    for r in event['rows'][:15]: # Print first 15 mapped
                        print(r)
                elif event["type"] in ["progress", "error"]:
                    print(f"[{event['type'].upper()}]: {event.get('message', '')}")
        except Exception as e:
            print(f"Failed extraction on {img}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
