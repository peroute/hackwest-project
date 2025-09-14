"""
Simplified database configuration: PostgreSQL + MongoDB Atlas.
PostgreSQL for user data and metadata, MongoDB Atlas for AI search.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL Database URL for user data
POSTGRES_URL = os.getenv("POSTGRES_URL", "sqlite:///./university_resources.db")

# MongoDB Atlas URL for AI search
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://username:password@cluster.mongodb.net/university_resources")

# Create SQLAlchemy engine
if POSTGRES_URL.startswith("sqlite"):
    postgres_engine = create_engine(POSTGRES_URL, connect_args={"check_same_thread": False})
else:
    postgres_engine = create_engine(POSTGRES_URL)

# Create SessionLocal class
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# Create Base class for PostgreSQL models
PostgresBase = declarative_base()

# MongoDB Atlas client for AI search
class MongoDBAtlas:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB Atlas."""
        try:
            from pymongo import MongoClient
            import ssl
            # Sync client for operations with SSL configuration
            self.client = MongoClient(
                MONGODB_URL,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True
            )
            self.db = self.client.university_resources
            self.collection = self.db.resources
            
            # Test connection
            self.client.admin.command('ping')
            print("Connected to MongoDB Atlas")
            
        except Exception as e:
            print(f"Could not connect to MongoDB Atlas: {e}")
            self.client = None
            self.db = None
            self.collection = None
    
    def add_document(self, document):
        """Add a document to MongoDB Atlas."""
        if self.collection is None:
            return False
        
        try:
            result = self.collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            print(f"Error adding document to MongoDB: {e}")
            return False
    
    def search_documents(self, query_vector, limit=5, score_threshold=0.7):
        """Search documents using vector similarity."""
        if self.collection is None:
            return []
        
        try:
            # Vector search using MongoDB Atlas Search
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_search_index",
                        "path": "embedding",
                        "queryVector": query_vector,
                        "numCandidates": limit * 10,
                        "limit": limit
                    }
                },
                {
                    "$addFields": {
                        "score": {"$meta": "vectorSearchScore"}
                    }
                },
                {
                    "$match": {
                        "score": {"$gte": score_threshold}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            return results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def update_document(self, document_id, document):
        """Update a document in MongoDB Atlas."""
        if self.collection is None:
            return False
        
        try:
            result = self.collection.update_one(
                {"_id": document_id},
                {"$set": document}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def delete_document(self, document_id):
        """Delete a document from MongoDB Atlas."""
        if self.collection is None:
            return False
        
        try:
            result = self.collection.delete_one({"_id": document_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

# Global MongoDB Atlas instance (lazy initialization)
mongodb_atlas = None

def get_mongodb_atlas_instance():
    """Get or create MongoDB Atlas instance."""
    global mongodb_atlas
    if mongodb_atlas is None:
        mongodb_atlas = MongoDBAtlas()
    return mongodb_atlas


def get_postgres_db():
    """
    Dependency to get PostgreSQL database session.
    """
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongodb_atlas():
    """
    Get MongoDB Atlas instance for AI search.
    """
    return get_mongodb_atlas_instance()


def get_database_status():
    """
    Get status of both databases.
    """
    status = {
        "postgresql": "connected",
        "mongodb_atlas": "connected"
    }
    
    # Test PostgreSQL
    try:
        db = PostgresSessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        status["postgresql"] = f"error: {str(e)}"
    
    # Test MongoDB Atlas
    try:
        mongodb_atlas = get_mongodb_atlas_instance()
        if mongodb_atlas.client:
            mongodb_atlas.client.admin.command('ping')
        else:
            status["mongodb_atlas"] = "not_connected"
    except Exception as e:
        status["mongodb_atlas"] = f"error: {str(e)}"
    
    return status