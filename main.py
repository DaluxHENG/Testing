from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import routes_upload, routes_analysis, routes_resume
from app.core.config import settings
from app.storage.file_manager import ensure_directories
import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(
    title="SmartRecruit API",
    description="AI-powered resume screening platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the frontend directory
STATIC_DIR = "frontend"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve favicon if it exists
@app.get("/favicon.ico")
async def favicon():
    path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(path):
        return FileResponse(path)
    return {"detail": "Favicon not found"}, 404

# Include API routes
app.include_router(routes_upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(routes_analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(routes_resume.router, prefix="/api/v1", tags=["resume"])

# Startup event
@app.on_event("startup")
async def startup_event():
    try:
        ensure_directories()
        logger.info("SmartRecruit API started successfully")
        logger.info(f"Server running on http://{settings.host}:{settings.port}")
    except Exception as e:
        logger.error(f"Failed to start SmartRecruit API: {e}")
        raise e

# Root endpoint
@app.get("/")
async def root():
    return {"message": "SmartRecruit API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SmartRecruit API"}

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
