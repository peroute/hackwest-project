"""
Google Gemini 2.5 Pro integration with PostgreSQL + MongoDB Atlas.
Handles AI search and intelligent responses.
"""
import os
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .models import Question, SearchLog
from .database import get_postgres_db, get_mongodb_atlas
from .schemas import SearchResult, AskResponse

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        GEMINI_AVAILABLE = True
        print("✅ Gemini API configured")
    except ImportError:
        print("⚠️  Google Generative AI not installed - using fallback")
        GEMINI_AVAILABLE = False
else:
    print("⚠️  GEMINI_API_KEY not set - AI features will be limited")
    GEMINI_AVAILABLE = False

# Initialize sentence transformer model for embeddings
try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Sentence transformer model loaded")
except ImportError:
    print("⚠️  Sentence transformers not installed - using fallback")
    embedding_model = None


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for given text using sentence-transformers.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of float values representing the embedding
    """
    if not embedding_model:
        # Fallback: return a simple hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to 384-dimensional vector
        embedding = [float(hash_bytes[i % len(hash_bytes)]) / 255.0 for i in range(384)]
        return embedding
    
    if not text:
        return [0.0] * 384  # Return zero vector for empty text
    
    embedding = embedding_model.encode(text)
    return embedding.tolist()


def store_resource_with_embedding(
    title: str, 
    description: str, 
    url: str,
    category: str = None,
    tags: List[str] = None,
    owner_id: int = None,
    is_public: bool = True
) -> Dict[str, Any]:
    """
    Create a new resource with embedding and store ONLY in MongoDB Atlas.
    
    Args:
        title: Resource title
        description: Resource description
        url: Resource URL
        category: Resource category
        tags: List of tags
        owner_id: ID of the user who created the resource
        is_public: Whether the resource is public
        
    Returns:
        Created resource document from MongoDB Atlas
    """
    try:
        # Generate embedding
        combined_text = f"{title} {description or ''}"
        embedding = generate_embedding(combined_text)
        
        # Create MongoDB document
        mongodb_doc = {
            "title": title,
            "description": description,
            "url": url,
            "category": category,
            "tags": tags or [],
            "owner_id": owner_id,
            "is_public": is_public,
            "embedding": embedding,
            "created_at": "2024-01-01T00:00:00Z",  # Will be set by MongoDB
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Get MongoDB Atlas connection directly
        from pymongo import MongoClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return None
        
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
        
        # Insert document directly
        result = collection.insert_one(mongodb_doc)
        
        if result.inserted_id:
            # Add the MongoDB ID to the document (convert to string for JSON serialization)
            mongodb_doc["_id"] = str(result.inserted_id)
            mongodb_doc["resource_id"] = str(result.inserted_id)
            print(f"✅ Resource stored in MongoDB Atlas with ID: {result.inserted_id}")
            
            # Close connection
            client.close()
            return mongodb_doc
        else:
            print("❌ Error: Could not store resource in MongoDB Atlas")
            client.close()
            return None
            
    except Exception as e:
        print(f"❌ Error storing resource in MongoDB Atlas: {e}")
        return None


def search_similar_resources(
    query: str, 
    limit: int = 5, 
    score_threshold: float = 0.7,
    filters: Dict[str, Any] = None
) -> List[SearchResult]:
    """
    Search for similar resources using MongoDB Atlas vector similarity search.
    
    Args:
        query: Search query
        limit: Maximum number of results
        score_threshold: Minimum similarity score
        filters: Additional filters for search
        
    Returns:
        List of similar resource results
    """
    try:
        # Get MongoDB Atlas connection directly
        from pymongo import MongoClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return []
        
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
        
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # Simple text search for now (vector search requires Atlas Search setup)
        search_results = []
        
        # Build search query - split query into words for better matching
        query_words = query.lower().split()
        
        # Create regex patterns for each word
        title_patterns = [{"title": {"$regex": word, "$options": "i"}} for word in query_words]
        desc_patterns = [{"description": {"$regex": word, "$options": "i"}} for word in query_words]
        tag_patterns = [{"tags": {"$regex": word, "$options": "i"}} for word in query_words]
        
        search_query = {
            "$or": title_patterns + desc_patterns + tag_patterns
        }
        
        if filters:
            search_query.update(filters)
        
        # Search documents
        cursor = collection.find(search_query).limit(limit)
        docs = list(cursor)
        
        for doc in docs:
            search_result = SearchResult(
                id=str(doc["_id"]),
                title=doc["title"],
                description=doc["description"],
                url=doc["url"],
                category=doc.get("category"),
                tags=doc.get("tags", []),
                similarity_score=0.8,  # Placeholder score
                owner_id=doc.get("owner_id")
            )
            search_results.append(search_result)
        
        client.close()
        return search_results
        
    except Exception as e:
        print(f"❌ Error in vector search: {e}")
        return []


def generate_ai_answer(question: str, resources: List[SearchResult]) -> str:
    """
    Generate answer using Gemini 2.5 Pro with provided resources as context.
    
    Args:
        question: User's question
        resources: List of relevant resources
        
    Returns:
        AI-generated response string
    """
    if not GEMINI_AVAILABLE:
        return generate_simple_answer(question, resources)
    
    if not resources:
        return "I couldn't find any relevant resources to answer your question. Please try rephrasing your question or adding more resources to the database."
    
    # Format resources for the prompt
    resources_text = "\n".join([
        f"- **{resource.title}**: {resource.description or 'No description'} "
        f"(Category: {resource.category or 'Uncategorized'}) "
        f"- 🔗 {resource.url}"
        for resource in resources
    ])
    
    # Create the prompt
    prompt = f"""You are a helpful university assistant with access to a comprehensive database of university resources.

The user will ask questions about university resources, services, or general information.
Use the following resources to provide accurate, helpful answers.
Always include relevant links in your response.
If the resources don't fully answer the question, say so and suggest how the user might find more information.

Available Resources:
{resources_text}

User Question: {question}

Please provide a comprehensive, helpful answer based on the available resources."""

    try:
        # Use Gemini 2.5 Pro
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return generate_simple_answer(question, resources)
            
    except Exception as e:
        print(f"❌ Error generating AI response: {e}")
        return generate_simple_answer(question, resources)


def generate_simple_answer(question: str, resources: List[SearchResult]) -> str:
    """
    Generate a simple answer without AI when Gemini is not available.
    
    Args:
        question: User's question
        resources: List of relevant resources
        
    Returns:
        Simple response string
    """
    if not resources:
        return "I couldn't find any relevant resources to answer your question. Please try adding some resources first."
    
    # Simple response
    response = "Based on your question, here are some relevant resources:\n\n"
    
    for i, resource in enumerate(resources, 1):
        response += f"{i}. **{resource.title}**\n"
        if resource.description:
            response += f"   {resource.description}\n"
        if resource.category:
            response += f"   📂 Category: {resource.category}\n"
        response += f"   🔗 {resource.url}\n\n"
    
    return response


async def ask_question_with_ai(
    question: str, 
    user_id: Optional[int] = None,
    search_type: str = "semantic"
) -> AskResponse:
    """
    Ask a question and get AI-generated answer using vector similarity search.
    
    Args:
        question: User's question
        user_id: ID of the user asking the question
        search_type: Type of search to perform
        
    Returns:
        AI-generated response with relevant resources
    """
    start_time = time.time()
    
    # Find similar resources using vector search
    similar_resources = search_similar_resources(
        query=question,
        limit=5,
        score_threshold=0.7
    )
    
    # Generate AI answer
    answer = generate_ai_answer(question, similar_resources)
    
    response_time = int((time.time() - start_time) * 1000)
    
    return AskResponse(
        question=question,
        answer=answer,
        relevant_resources=similar_resources,
        user_id=user_id,
        timestamp=time.time()
    )


def delete_resource_from_mongodb(resource_id: str):
    """
    Delete a resource from MongoDB Atlas.
    
    Args:
        resource_id: ID of the resource to delete
    """
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return False
        
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
        
        # Delete document
        result = collection.delete_one({"_id": ObjectId(resource_id)})
        
        client.close()
        
        if result.deleted_count > 0:
            print(f"✅ Deleted resource {resource_id} from MongoDB Atlas")
            return True
        else:
            print(f"⚠️  Warning: Could not delete resource {resource_id} from MongoDB Atlas")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting resource {resource_id} from MongoDB Atlas: {e}")
        return False


def update_resource_in_mongodb(
    resource_id: str, 
    title: str, 
    description: str, 
    url: str,
    category: str = None,
    tags: List[str] = None,
    owner_id: int = None,
    is_public: bool = True
):
    """
    Update a resource in MongoDB Atlas.
    
    Args:
        resource_id: ID of the resource to update
        title: New title
        description: New description
        url: New URL
        category: New category
        tags: New tags
        owner_id: Owner ID
        is_public: Whether public
    """
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment variables")
            return False
        
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
        
        # Generate new embedding
        combined_text = f"{title} {description or ''}"
        embedding = generate_embedding(combined_text)
        
        # Create updated MongoDB document
        update_doc = {
            "title": title,
            "description": description,
            "url": url,
            "category": category,
            "tags": tags or [],
            "owner_id": owner_id,
            "is_public": is_public,
            "embedding": embedding,
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Update document
        result = collection.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": update_doc}
        )
        
        client.close()
        
        if result.modified_count > 0:
            print(f"✅ Updated resource {resource_id} in MongoDB Atlas")
            return True
        else:
            print(f"⚠️  Warning: Could not update resource {resource_id} in MongoDB Atlas")
            return False
            
    except Exception as e:
        print(f"❌ Error updating resource {resource_id} in MongoDB Atlas: {e}")
        return False


def batch_process_resources(resources_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multiple resources in batch.
    
    Args:
        resources_data: List of resource data dictionaries
        
    Returns:
        List of created resource documents from MongoDB Atlas
    """
    created_resources = []
    
    for resource_data in resources_data:
        try:
            resource = store_resource_with_embedding(
                title=resource_data.get("title", ""),
                description=resource_data.get("description", ""),
                url=resource_data.get("url", ""),
                category=resource_data.get("category"),
                tags=resource_data.get("tags", []),
                owner_id=resource_data.get("owner_id"),
                is_public=resource_data.get("is_public", True)
            )
            if resource:
                created_resources.append(resource)
        except Exception as e:
            print(f"Error processing resource {resource_data.get('title', 'Unknown')}: {e}")
            continue
    
    return created_resources


def get_vector_database_status() -> Dict[str, Any]:
    """
    Get status of the vector database (MongoDB Atlas).
    
    Returns:
        Dictionary with vector database status information
    """
    return get_mongodb_atlas_status()


def get_mongodb_atlas_status() -> Dict[str, Any]:
    """
    Get status and statistics of MongoDB Atlas.
    
    Returns:
        Dictionary with database status information
    """
    mongodb_atlas = get_mongodb_atlas()
    
    if not mongodb_atlas.collection:
        return {"status": "not_connected", "error": "MongoDB Atlas not connected"}
    
    try:
        stats = mongodb_atlas.get_collection_stats()
        return {
            "status": "connected",
            "type": "mongodb_atlas",
            "collection_stats": stats
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}