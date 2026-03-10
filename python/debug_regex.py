import re

BOOTH_PATTERNS = [
    r"\b([A-Z]{1,3}\d[A-Z]\d{2,3})\b",           # SAJ09, S1A13, SAK07
    r"\b([A-Z]{1,3}[-_]?[A-Z][-_]?\d{2,3})\b",   # AR-E10, AR-F10, S1-A40
    r"\b(\d{1,2}[A-Z]\d{1,3})\b",                 # 6A31, 7A32, 6B30
    r"\b(\d{1,2}[-_][A-Z])\b",                    # 1-A, 2-B, 1-F
    r"\b([A-Z]\d{1,3})\b",                        # A7, G24, M12
    r"\b(\d{3,5}[A-Z]?)\b",                       # 4240, 4230, 1234A
    r"\b(?:ST(?:AND)?|BOOTH)\s*[-:]?\s*([A-Z0-9\-_]{1,10})\b", # STAND 102, BOOTH 42
    r"\b([A-Z]{1,2}[-_]?\d{1,4})\b",              # A12, B-14, C3
    r"^(?:\s*)(\d{1,3})(?:\s*)$",                 # Standalone short numbers like 16, 18
]

test_string = "18\nStartup Vision\n6x6\n1-A"
lines = test_string.split('\n')
for line in lines:
    for p in BOOTH_PATTERNS:
        m = re.search(p, line, re.IGNORECASE)
        if m:
            print(f"Line '{line}' matched `{p}` -> Group 1: {m.group(1)}")
