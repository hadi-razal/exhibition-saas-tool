# ExhibitIQ — Project Memory

## Stack
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS 4, shadcn/ui
- **Backend**: Python FastAPI (port 8000), proxied via Next.js API routes
- **Extraction**: Python-only (no Anthropic/AI API) — OCR + spatial block grouping

## Key File Paths
- Frontend pages: `src/app/page.tsx`, `src/app/dashboard/floorplan/page.tsx`
- Theme: `src/app/globals.css` (white/light premium theme, oklch colors)
- Layout: `src/app/layout.tsx` — NO dark class on html element
- Navbar: `src/components/layout/navbar.tsx` — light theme
- OCR Engine: `python/floorplan/ocr_engine.py` — PSM 11 multipass + spatial clustering
- PDF Parser: `python/floorplan/pdf_parser.py` — spatial block extraction via PyMuPDF
- Pattern Matcher: `python/floorplan/pattern_matcher.py` — block-level extraction + NON_EXHIBITOR blocklist
- Extractor: `python/floorplan/extractor.py` — orchestrates vector path then OCR fallback
- FastAPI server: `python/main.py`

## Theme — Premium White/Light
- Background: off-white `oklch(0.99 0.004 240)`
- Primary: deep cobalt blue `oklch(0.42 0.200 250)`
- Chart-2 accent: teal `oklch(0.52 0.160 185)`
- Custom classes: `.card-elevated`, `.card-tinted`, `.surface-muted`, `.hero-bg`, `.dot-grid`, `.gradient-text`, `.tag-blue`, `.tag-teal`, `.tag-neutral`
- NO dark mode — pure light theme

## Floor Plan Extraction Pipeline
1. **Vector PDFs** (embedded text): PyMuPDF `get_text("blocks")` → spatial text blocks → pattern match per block
2. **Image PDFs / scans**: pdf2image + Tesseract PSM 11 (sparse text) + spatial clustering → pattern match per cluster
3. **Image files**: Same as above but single image

## Extraction Fields
- booth_number, exhibitor_name (empty string if not shown), booth_size, area_sqm, hall, zone, source
- source = "vector" | "block" | "ocr" | "table"

## Filtering
- 60+ non-exhibitor terms blocked (toilets, entrances, corridors, registration, networking zones, etc.)
- Booth-only rows (no exhibitor name) still appear — shown as "No name listed" in UI

## User Preferences
- Python-only — no Anthropic/external AI API
- White/light premium design (not dark)
- All possible data: booth no., name, dimensions, area m²
- Non-exhibitor terms filtered out; booth-only rows kept
