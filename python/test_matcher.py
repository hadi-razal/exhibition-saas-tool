import sys
sys.path.append(r"c:\Users\hadhi\Desktop\Personal\Programming\exhibition-saas-tool\python")

from floorplan.pattern_matcher import PatternMatcher
from pprint import pprint

def test_pattern_matcher():
    pm = PatternMatcher()
    
    # Test cases that previously failed or were edge cases
    test_blocks = [
        # 1. Long name truncation test + Short booth number
        "16\nDEWA SUSTAINABILITY SEMINAR",
        
        # 2. Complex booth format (e.g. 1-A or A7)
        "1-A\nMicrosoft Corporation\n6x6",
        
        # 3. Non-exhibitor filtering
        "Hall 1\nCafe",
        "Entrance\nMain Entrance",
        
        # 4. Dimension parsing
        "SAJ17\nApple Inc.\n16x15 m\n150 sqm",
        
        # 5. Short numeric booth
        "18\nStartup Vision"
    ]
    
    print("\n\n--- Testing Pattern Matcher (Extracted Blocks) ---")
    rows = pm.extract_from_blocks(test_blocks, 1)
    
    print(f"Extracted {len(rows)} valid booths:")
    for row in rows:
        pprint(row)

if __name__ == "__main__":
    test_pattern_matcher()
