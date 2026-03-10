"""
ExhibitIQ — Python Processing Server
FastAPI server providing floor plan extraction and web scraping endpoints.
"""
import os
import json
import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from floorplan.extractor import FloorPlanExtractor
from scraper.scraper_engine import ScraperEngine
from utils.export import export_to_csv, export_to_excel, export_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("exhibitiq")

app = FastAPI(
    title="ExhibitIQ Processing Server",
    description="Backend processing for floor plan OCR extraction and exhibitor web scraping",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ===================== Floor Plan Endpoints =====================

@app.post("/api/floorplan/extract")
async def extract_floorplan(file: UploadFile = File(...)):
    """Extract structured data from a floor plan file using OCR and text parsing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Save uploaded file temporarily
    temp_path = UPLOAD_DIR / file.filename
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        extractor = FloorPlanExtractor()

        async def generate():
            try:
                async for event in extractor.extract(str(temp_path)):
                    yield f"data: {json.dumps(event)}\n\n"
            except Exception as e:
                logger.error(f"Extraction error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            finally:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


class ExportRequest(BaseModel):
    rows: list[dict]
    format: str


@app.post("/api/floorplan/export")
async def export_floorplan(req: ExportRequest):
    """Export floor plan results to CSV, Excel, or JSON."""
    return _handle_export(req, "floorplan-results")


# ===================== Scraper Endpoints =====================

class AnalyzeRequest(BaseModel):
    url: str


class ScrapeRequest(BaseModel):
    url: str
    max_pages: int = 10
    follow_detail_pages: bool = True
    extract_contacts: bool = True


@app.post("/api/scraper/analyze")
async def analyze_url(req: AnalyzeRequest):
    """Analyze an exhibitor directory page to detect structure, pagination, and detail pages."""
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        engine = ScraperEngine()
        result = await engine.analyze(req.url.strip())
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scraper/scrape")
async def scrape_exhibitors(req: ScrapeRequest):
    """Scrape exhibitor data from a directory URL with pagination and detail page support."""
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    engine = ScraperEngine()

    async def generate():
        try:
            async for event in engine.scrape(
                url=req.url.strip(),
                max_pages=req.max_pages,
                follow_detail_pages=req.follow_detail_pages,
                extract_contacts=req.extract_contacts,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/scraper/export")
async def export_scraper(req: ExportRequest):
    """Export scraper results to CSV, Excel, or JSON."""
    return _handle_export(req, "exhibitor-scrape-results")


# ===================== Export Helper =====================

def _handle_export(req: ExportRequest, filename_prefix: str):
    """Handle export for both floor plan and scraper results."""
    if not req.rows:
        raise HTTPException(status_code=400, detail="No data to export")

    try:
        if req.format == "csv":
            content = export_to_csv(req.rows)
            return StreamingResponse(
                iter([content]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename_prefix}.csv"},
            )
        elif req.format == "excel":
            content = export_to_excel(req.rows)
            return StreamingResponse(
                iter([content]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename_prefix}.xlsx"},
            )
        elif req.format == "json":
            content = export_to_json(req.rows)
            return StreamingResponse(
                iter([content]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename_prefix}.json"},
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {req.format}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== Health Check =====================

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ExhibitIQ Processing Server"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
