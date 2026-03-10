# ExhibitIQ — Exhibition Intelligence Platform

**Extract floor plan data. Scrape exhibitor directories. Export clean datasets.**

A local-first MVP built for exhibition professionals — stand builders, agencies, marketing teams, logistics companies, and exhibition sales teams.

---

## ✨ Key Features

### 🗺️ Floor Plan OCR Extractor
- Upload PDF, PNG, JPG floor plans
- Multi-layered extraction: direct PDF text → OCR fallback → regex pattern matching
- Extracts booth numbers, sizes, exhibitor names, halls, zones
- Image preprocessing (grayscale, denoise, contrast, sharpen)
- Export to CSV, Excel, JSON

### 🌐 Exhibitor Web Scraper
- Paste any exhibitor directory URL
- **Two-phase flow**: Analyze page → confirm settings → full scrape
- Auto-detects pagination, detail pages, listing structure
- Extracts company names, booth numbers, contacts, LinkedIn, social links
- Handles static HTML and JavaScript-rendered pages (Playwright)
- Pagination traversal and detail page following
- Export to CSV, Excel, JSON

---

## 📁 Project Structure

```
exhibition-platform/
├── src/                          # Next.js frontend
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   ├── layout.tsx            # Root layout
│   │   ├── pricing/page.tsx      # Pricing page
│   │   ├── about/page.tsx        # About page
│   │   ├── dashboard/
│   │   │   ├── page.tsx          # Dashboard
│   │   │   ├── floorplan/page.tsx # Floor Plan Extractor
│   │   │   └── scraper/page.tsx  # Exhibitor Scraper
│   │   └── api/
│   │       ├── floorplan/        # Proxy to Python API
│   │       └── scraper/          # Proxy to Python API
│   └── components/
│       ├── layout/               # Navbar, Footer
│       └── ui/                   # shadcn/ui components
├── python/                       # Python processing backend
│   ├── main.py                   # FastAPI server (port 8000)
│   ├── requirements.txt          # Python dependencies
│   ├── floorplan/
│   │   ├── extractor.py          # Extraction orchestrator
│   │   ├── pdf_parser.py         # PDF text extraction + image conversion
│   │   ├── ocr_engine.py         # OCR with image preprocessing
│   │   └── pattern_matcher.py    # Regex for booth codes, sizes, halls
│   ├── scraper/
│   │   └── scraper_engine.py     # Web scraper (analyze + scrape)
│   └── utils/
│       └── export.py             # CSV, Excel, JSON export
└── .env.local                    # Environment config
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Tesseract OCR** installed on your system
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
  - Mac: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`
- **Poppler** (for PDF-to-image conversion)
  - Windows: [Download](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH
  - Mac: `brew install poppler`
  - Linux: `sudo apt install poppler-utils`

### 1. Install Frontend

```bash
cd exhibition-platform
npm install
```

### 2. Install Python Dependencies

```bash
cd python
pip install -r requirements.txt

# For dynamic scraping (optional):
playwright install chromium
```

### 3. Start Python Server

```bash
cd python
python main.py
```

The Python server runs at `http://localhost:8000`.

### 4. Start Frontend

```bash
# In a new terminal
cd exhibition-platform
npm run dev
```

The app runs at `http://localhost:3000`.

---

## 🔧 Environment Variables

Create `.env.local` in the project root:

```env
PYTHON_API_URL=http://localhost:8000
```

When deploying, change this to your Python server's URL.

---

## 📖 How Data Extraction Works

### Floor Plan Extraction Pipeline

1. **File Upload** → Detect file type (PDF vs image)
2. **Layer 1: PDF Text** → Direct text extraction via PyMuPDF / pdfplumber
3. **Layer 2: OCR** → Convert to image → preprocess → pytesseract
4. **Layer 3: Patterns** → Regex matches booth codes (`A12`, `B-14`, `H5-B13`), sizes (`3x3`, `12 sqm`), halls, zones
5. **Output** → Structured rows with booth number, exhibitor, size, hall, etc.

### Web Scraper Pipeline

1. **Analyze** → Load URL → detect pagination, detail pages, listing structure
2. **Confirm** → User reviews settings (max pages, follow details, extract contacts)
3. **Scrape** → Traverse pages → extract exhibitor blocks → follow detail pages
4. **Normalize** → Clean, deduplicate, structure
5. **Output** → Exhibitor rows with name, booth, country, email, LinkedIn, etc.

---

## ⚠️ Known Limitations

- **OCR accuracy** depends on image quality and resolution
- **Complex floor plans** with overlapping elements may need manual review
- **JavaScript-heavy sites** require Playwright (install separately)
- **Anti-scraping protections** may block some websites
- **Tesseract and Poppler** must be installed as system dependencies

---

## 🔮 Future Improvements

- AI-powered booth boundary detection
- Multi-language OCR support
- Batch processing for multiple floor plans
- Scheduled scraping jobs
- CRM integrations
- Cloud-hosted processing
- Authentication and team features
- API access for programmatic use

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | Python 3.11+, FastAPI, uvicorn |
| OCR | pytesseract, OpenCV, pdf2image, PyMuPDF, pdfplumber |
| Scraping | requests, BeautifulSoup, lxml, Playwright |
| Export | pandas, openpyxl |
| Communication | SSE (Server-Sent Events) for real-time progress |

---

Built for the exhibition industry.
