from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .api.routes import router as api_router
from .core.config import get_settings
from .storage.db import create_tables
from .utils.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Shadow Engine starting up...")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shadow Engine shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Enterprise-grade cybersecurity decision engine",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routes
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Shadow Engine",
        "version": settings.API_VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
