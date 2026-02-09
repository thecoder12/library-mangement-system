"""REST API Server for the Neighborhood Library Service."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import books_router, members_router, borrows_router
from app.logging_config import setup_logging, get_logger
from app.middleware import RequestLoggingMiddleware

# Configure structured logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Neighborhood Library API",
    description="REST API for the Neighborhood Library Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add request logging middleware (must be added first)
app.add_middleware(RequestLoggingMiddleware)

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
    logger.info(
        "REST API server starting",
        extra={
            "host": settings.rest_host,
            "port": settings.rest_port,
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "log_file": settings.log_file,
        }
    )
    logger.info(f"API Documentation available at http://{settings.rest_host}:{settings.rest_port}/docs")
    
    uvicorn.run(
        "rest_server:app",
        host=settings.rest_host,
        port=settings.rest_port,
        reload=False,
        log_level="warning",  # Reduce uvicorn noise, we have our own logging
    )


if __name__ == "__main__":
    serve()
