"""
FastAPI application with hybrid PostgreSQL + Qdrant architecture.
Supports large-scale vector search and user management.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from .routers import resources, ask, users, search, analytics, upload
from .database import postgres_engine, PostgresBase, get_database_status
from .models import User, Question, SearchLog

# Load environment variables
load_dotenv()

# Create PostgreSQL database tables
PostgresBase.metadata.create_all(bind=postgres_engine)

# Initialize FastAPI app
app = FastAPI(
    title="University Resources API",
    description="Hybrid API with PostgreSQL + MongoDB Atlas for large-scale resource management and AI-powered search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resources.router, prefix="/api/v1")
app.include_router(ask.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "University Resources API",
        "version": "1.0.0",
        "architecture": "PostgreSQL + MongoDB Atlas",
        "docs": "/docs",
        "endpoints": {
            "resources": "/api/v1/resources/",
            "ask": "/api/v1/ask/",
            "users": "/api/v1/users/",
            "search": "/api/v1/search/",
            "analytics": "/api/v1/analytics/",
            "upload": "/api/v1/upload/"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database status."""
    db_status = get_database_status()
    
    return {
        "status": "healthy",
        "databases": db_status,
        "version": "1.0.0"
    }


@app.get("/status")
async def get_status():
    """Detailed status endpoint with system information."""
    from .gemini import get_vector_database_status
    
    db_status = get_database_status()
    vector_status = get_vector_database_status()
    
    return {
        "status": "operational",
        "databases": db_status,
        "vector_database": vector_status,
        "version": "1.0.0",
        "features": [
            "PostgreSQL for user data",
            "Qdrant for vector search",
            "Gemini AI integration",
            "Large-scale data support",
            "Advanced search capabilities"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)