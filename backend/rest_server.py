"""REST API Server for the Neighborhood Library Service."""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import books_router, members_router, borrows_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Neighborhood Library API",
    description="REST API for the Neighborhood Library Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books_router)
app.include_router(members_router)
app.include_router(borrows_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Neighborhood Library API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def serve():
    """Start the REST API server."""
    logger.info(f"🚀 REST API server starting on http://{settings.rest_host}:{settings.rest_port}")
    logger.info(f"📚 API Documentation available at http://{settings.rest_host}:{settings.rest_port}/docs")
    
    uvicorn.run(
        "rest_server:app",
        host=settings.rest_host,
        port=settings.rest_port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    serve()
