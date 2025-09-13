"""
File upload endpoints for bulk resource import
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
import json
from ..gemini import store_resource_with_embedding

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/json")
async def upload_json_file(file: UploadFile = File(...)):
    """
    Upload and process a JSON file containing resources.
    """
    try:
        # Check file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be a JSON file")
        
        # Read file content
        content = await file.read()
        data = json.loads(content)
        
        # Process the data
        results = await process_ttu_resources(data)
        
        return {
            "message": "Resources uploaded successfully",
            "total_processed": results["total_processed"],
            "total_categories": results["total_categories"],
            "successful": results["successful"],
            "failed": results["failed"],
            "details": results["details"]
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def process_ttu_resources(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process TTU resources JSON data and store in MongoDB Atlas.
    """
    results = {
        "total_processed": 0,
        "total_categories": 0,
        "successful": 0,
        "failed": 0,
        "details": []
    }
    
    # Process each category
    for category_name, resources in data.items():
        if not isinstance(resources, list):
            continue
            
        results["total_categories"] += 1
        category_results = {
            "category": category_name.strip(),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process each resource in the category
        for resource in resources:
            if not isinstance(resource, dict):
                continue
                
            results["total_processed"] += 1
            category_results["processed"] += 1
            
            try:
                # Extract resource data
                title = resource.get("title", "").strip()
                description = resource.get("text", "").strip()
                url = resource.get("url", "").strip()
                
                if not title or not url:
                    category_results["failed"] += 1
                    category_results["errors"].append(f"Missing required fields: {title[:50]}...")
                    continue
                
                # Create tags from category and title
                tags = [category_name.strip().lower()]
                if title:
                    # Add words from title as tags
                    title_words = [word.lower() for word in title.split() if len(word) > 3]
                    tags.extend(title_words[:5])  # Limit to 5 words
                
                # Store resource in MongoDB Atlas
                created_resource = store_resource_with_embedding(
                    title=title,
                    description=description,
                    url=url,
                    category=category_name.strip(),
                    tags=tags,
                    owner_id=None,
                    is_public=True
                )
                
                if created_resource:
                    results["successful"] += 1
                    category_results["successful"] += 1
                else:
                    results["failed"] += 1
                    category_results["failed"] += 1
                    category_results["errors"].append(f"Failed to store: {title[:50]}...")
                    
            except Exception as e:
                results["failed"] += 1
                category_results["failed"] += 1
                category_results["errors"].append(f"Error processing {title[:50] if 'title' in resource else 'unknown'}: {str(e)}")
        
        results["details"].append(category_results)
    
    return results


@router.post("/ttu-resources")
async def upload_ttu_resources():
    """
    Upload the specific TTU resources from the JSON file.
    """
    try:
        # Read the ttu_resources.json file
        with open("ttu_resources.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Process the data
        results = await process_ttu_resources(data)
        
        return {
            "message": "TTU resources uploaded successfully",
            "total_processed": results["total_processed"],
            "total_categories": results["total_categories"],
            "successful": results["successful"],
            "failed": results["failed"],
            "details": results["details"]
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ttu_resources.json file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")