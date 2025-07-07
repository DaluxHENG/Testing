from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from app.api import routes_upload, routes_analysis, routes_resume, routes_batch
from app.core.config import settings
from app.storage.file_manager import ensure_directories
import uvicorn
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartRecruit API",
    description="AI-powered resume screening platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for CSS, JS, and other assets
STATIC_DIR = "frontend" 
app.mount("/css", StaticFiles(directory=f"{STATIC_DIR}/css"), name="css")
app.mount("/js", StaticFiles(directory=f"{STATIC_DIR}/js"), name="js")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve HTML files
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse(f"{STATIC_DIR}/index.html")

@app.get("/index.html")
async def redirect_index():
    return RedirectResponse(url="/")

@app.get("/upload.html", response_class=HTMLResponse)
async def serve_upload():
    return FileResponse(f"{STATIC_DIR}/upload.html")

@app.get("/upload.html", response_class=HTMLResponse)
async def get_upload():
    return FileResponse(f"{STATIC_DIR}/upload.html")


@app.get("/results.html", response_class=HTMLResponse)
async def serve_results():
    return FileResponse(f"{STATIC_DIR}/results.html")

@app.get("/batch.html", response_class=HTMLResponse)
async def serve_batch():
    return FileResponse(f"{STATIC_DIR}/batch.html")

# Include API routes
app.include_router(routes_upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(routes_analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(routes_resume.router, prefix="/api/v1", tags=["resume"])
app.include_router(routes_batch.router, prefix="/api/v1", tags=["batch"])

@app.on_event("startup")
async def startup_event():
    try:
        ensure_directories()
        logger.info("SmartRecruit API started successfully")
        logger.info(f"Server running on http://localhost:8000")
    except Exception as e:
        logger.error(f"Failed to start SmartRecruit API: {e}")
        raise e

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SmartRecruit API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)