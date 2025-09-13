"""
Advanced search endpoints with vector similarity search.
Supports both semantic and keyword search with Qdrant integration.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_postgres_db
from ..schemas import SearchRequest, SearchResponse, SearchResult, VectorSearchRequest, VectorSearchResponse
from ..gemini import search_similar_resources, get_vector_database_status

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
async def search_resources(
    search_request: SearchRequest,
    db: Session = Depends(get_postgres_db)
):
    """
    Simple search endpoint that searches for resources using MongoDB Atlas.
    """
    try:
        # Perform search using MongoDB Atlas
        results = search_similar_resources(
            query=search_request.query,
            limit=search_request.limit,
            score_threshold=search_request.score_threshold
        )
        
        return SearchResponse(
            query=search_request.query,
            results=results,
            total_results=len(results),
            search_type="mongodb"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    search_request: SearchRequest,
    db: Session = Depends(get_postgres_db)
):
    """
    Perform semantic search using vector similarity.
    """
    try:
        # Perform vector search
        results = search_similar_resources(
            query=search_request.query,
            limit=search_request.limit,
            score_threshold=search_request.score_threshold
        )
        
        return SearchResponse(
            query=search_request.query,
            results=results,
            total_results=len(results),
            search_type="semantic"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/vector", response_model=VectorSearchResponse)
async def vector_search(search_request: VectorSearchRequest):
    """
    Perform direct vector search in Qdrant.
    """
    try:
        from ..database import get_vector_db
        from ..gemini import generate_embedding
        
        vector_db = get_vector_db()
        
        if not vector_db.client:
            raise HTTPException(
                status_code=503,
                detail="Vector database not available"
            )
        
        # Generate embedding for query
        query_embedding = generate_embedding(search_request.query)
        
        # Search in Qdrant
        results = vector_db.search_vectors(
            query_embedding=query_embedding,
            limit=search_request.limit,
            score_threshold=search_request.score_threshold
        )
        
        # Get collection info
        collection_info = vector_db.get_collection_info()
        
        return VectorSearchResponse(
            query=search_request.query,
            results=results,
            total_results=len(results),
            collection_info=collection_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vector search failed: {str(e)}"
        )


@router.get("/status")
async def get_search_status():
    """
    Get search system status and statistics.
    """
    try:
        vector_status = get_vector_database_status()
        
        return {
            "status": "operational",
            "vector_database": vector_status,
            "search_types": ["semantic", "vector", "keyword"],
            "features": [
                "Vector similarity search",
                "Semantic understanding",
                "Large-scale data support",
                "Real-time search"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )


@router.get("/collections")
async def get_collections():
    """
    Get information about Qdrant collections.
    """
    try:
        from ..database import get_vector_db
        
        vector_db = get_vector_db()
        
        if not vector_db.client:
            raise HTTPException(
                status_code=503,
                detail="Vector database not available"
            )
        
        collections = vector_db.client.get_collections()
        
        return {
            "collections": [
                {
                    "name": collection.name,
                    "status": collection.status,
                    "points_count": collection.points_count,
                    "vectors_count": collection.vectors_count
                }
                for collection in collections.collections
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collections: {str(e)}"
        )
