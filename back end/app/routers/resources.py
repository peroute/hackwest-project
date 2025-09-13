"""
Resources API router for CRUD operations on university resources.
All resources stored in MongoDB Atlas only, PostgreSQL used for user data only.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..database import get_postgres_db, get_mongodb_atlas
from ..schemas import Resource, ResourceCreate, ResourceUpdate, BatchResourceCreate, BatchResourceResponse
from ..gemini import store_resource_with_embedding, update_resource_in_mongodb, delete_resource_from_mongodb, search_similar_resources

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/")
async def create_resource(resource: ResourceCreate):
    """
    Create a new resource with embedding in MongoDB Atlas only.
    """
    try:
        print(f"🔍 Creating resource: {resource.title}")
        
        # Store resource with embedding in MongoDB Atlas
        created_resource = store_resource_with_embedding(
            title=resource.title,
            description=resource.description,
            url=resource.url,
            category=resource.category,
            tags=resource.tags,
            owner_id=resource.owner_id,
            is_public=resource.is_public
        )
        
        print(f"🔍 Created resource result: {created_resource}")
        
        if not created_resource:
            print("❌ Created resource is None")
            raise HTTPException(status_code=500, detail="Failed to create resource in MongoDB Atlas")
        
        print("✅ Returning created resource")
        return created_resource
    except Exception as e:
        print(f"❌ Exception in create_resource: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating resource: {str(e)}")


@router.get("/", response_model=List[Dict[str, Any]])
async def list_resources(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List resources from MongoDB Atlas with optional filtering.
    """
    try:
        from pymongo import MongoClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            raise HTTPException(status_code=500, detail="MongoDB URL not configured")
        
        # Connect to MongoDB Atlas
        client = MongoClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Get database and collection
        db = client.university_resources
        collection = db.resources
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        
        # Get resources from MongoDB Atlas
        cursor = collection.find(query).skip(skip).limit(limit)
        resources = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for resource in resources:
            resource["_id"] = str(resource["_id"])
            if "resource_id" not in resource:
                resource["resource_id"] = str(resource["_id"])
        
        client.close()
        print(f"🔍 Found {len(resources)} resources")
        return resources
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing resources: {str(e)}")


@router.get("/{resource_id}", response_model=Dict[str, Any])
async def get_resource(resource_id: str):
    """
    Get a specific resource by ID from MongoDB Atlas.
    """
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            raise HTTPException(status_code=500, detail="MongoDB URL not configured")
        
        # Connect to MongoDB Atlas
        client = MongoClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Get database and collection
        db = client.university_resources
        collection = db.resources
        
        # Get resource from MongoDB Atlas
        resource = collection.find_one({"_id": ObjectId(resource_id)})
        
        client.close()
        
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Convert ObjectId to string
        resource["_id"] = str(resource["_id"])
        if "resource_id" not in resource:
            resource["resource_id"] = str(resource["_id"])
        
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting resource: {str(e)}")


@router.put("/{resource_id}", response_model=Dict[str, Any])
async def update_resource(
    resource_id: str,
    resource: ResourceUpdate
):
    """
    Update a resource in MongoDB Atlas.
    """
    try:
        # Update resource in MongoDB Atlas
        success = update_resource_in_mongodb(
            resource_id=resource_id,
            title=resource.title,
            description=resource.description,
            url=resource.url,
            category=resource.category,
            tags=resource.tags,
            owner_id=resource.owner_id,
            is_public=resource.is_public
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update resource in MongoDB Atlas")
        
        # Get updated resource
        mongodb_atlas = get_mongodb_atlas()
        updated_resource = mongodb_atlas.collection.find_one({"_id": resource_id})
        
        if not updated_resource:
            raise HTTPException(status_code=404, detail="Resource not found after update")
        
        # Convert ObjectId to string
        updated_resource["_id"] = str(updated_resource["_id"])
        if "resource_id" not in updated_resource:
            updated_resource["resource_id"] = str(updated_resource["_id"])
        
        return updated_resource
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resource: {str(e)}")


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str):
    """
    Delete a resource from MongoDB Atlas.
    """
    try:
        # Delete resource from MongoDB Atlas
        success = delete_resource_from_mongodb(resource_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete resource from MongoDB Atlas")
        
        return {"message": "Resource deleted successfully", "resource_id": resource_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resource: {str(e)}")


@router.post("/batch", response_model=BatchResourceResponse)
async def create_resources_batch(batch_data: BatchResourceCreate):
    """
    Create multiple resources in batch in MongoDB Atlas.
    """
    created_resources = []
    errors = []
    
    for i, resource_data in enumerate(batch_data.resources):
        try:
            created_resource = store_resource_with_embedding(
                title=resource_data.title,
                description=resource_data.description,
                url=resource_data.url,
                category=resource_data.category,
                tags=resource_data.tags,
                owner_id=resource_data.owner_id,
                is_public=resource_data.is_public
            )
            
            if created_resource:
                created_resources.append(created_resource)
            else:
                errors.append(f"Resource {i+1}: Failed to create")
                
        except Exception as e:
            errors.append(f"Resource {i+1}: {str(e)}")
    
    return BatchResourceResponse(
        created_count=len(created_resources),
        total_count=len(batch_data.resources),
        resources=created_resources,
        errors=errors
    )


@router.get("/search/semantic")
async def search_resources_semantic(
    query: str,
    limit: int = 5,
    score_threshold: float = 0.7
):
    """
    Search resources using semantic similarity in MongoDB Atlas.
    """
    try:
        # Use the search function from gemini.py
        results = search_similar_resources(
            query=query,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching resources: {str(e)}")