"""
Pydantic models for request/response validation.
Supports both PostgreSQL metadata and Qdrant vector operations.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Resource Schemas
class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    is_public: bool = True


class ResourceCreate(ResourceBase):
    owner_id: Optional[int] = None


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class Resource(ResourceBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Question Schemas
class QuestionBase(BaseModel):
    question_text: str


class QuestionCreate(QuestionBase):
    resource_id: Optional[int] = None


class Question(QuestionBase):
    id: int
    answer_text: Optional[str] = None
    user_id: Optional[int] = None
    resource_id: Optional[int] = None
    similarity_score: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


# Search Schemas
class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    score_threshold: float = 0.7
    search_type: str = "semantic"  # semantic, keyword, hybrid


class SearchResult(BaseModel):
    id: str  # Changed from int to str for MongoDB ObjectId
    title: str
    description: Optional[str] = None
    url: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    similarity_score: float
    owner_id: Optional[int] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_type: str
    response_time_ms: Optional[int] = None


# AI Response Schemas
class AskRequest(BaseModel):
    question: str
    user_id: Optional[int] = None
    search_type: str = "semantic"


class AskResponse(BaseModel):
    question: str
    answer: str
    relevant_resources: List[SearchResult]
    user_id: Optional[int] = None
    timestamp: datetime


# Vector Search Schemas
class VectorSearchRequest(BaseModel):
    query: str
    limit: int = 5
    score_threshold: float = 0.7
    filters: Optional[Dict[str, Any]] = None


class VectorSearchResult(BaseModel):
    id: int
    score: float
    payload: Dict[str, Any]


class VectorSearchResponse(BaseModel):
    query: str
    results: List[VectorSearchResult]
    total_results: int
    collection_info: Optional[Dict[str, Any]] = None


# Analytics Schemas
class SearchLogCreate(BaseModel):
    query: str
    results_count: int
    user_id: Optional[int] = None
    search_type: str = "semantic"
    response_time_ms: Optional[int] = None


class SearchLog(SearchLogCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Database Status Schema
class DatabaseStatus(BaseModel):
    postgresql: str
    qdrant: str
    collection_info: Optional[Dict[str, Any]] = None


# Batch Operations Schemas
class BatchResourceCreate(BaseModel):
    resources: List[ResourceCreate]


class BatchResourceResponse(BaseModel):
    created: int
    failed: int
    errors: List[str] = []


# Health Check Schema
class HealthCheck(BaseModel):
    status: str
    databases: DatabaseStatus
    version: str = "1.0.0"