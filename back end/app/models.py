"""
Database models for PostgreSQL + MongoDB Atlas architecture.
PostgreSQL stores user data and metadata, MongoDB Atlas stores vector embeddings for AI search.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import PostgresBase

# PostgreSQL Models for User Data and Metadata

class User(PostgresBase):
    """
    User model for authentication and user management.
    Stored in PostgreSQL.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    questions = relationship("Question", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# Resource model removed - all resources stored in MongoDB Atlas only


class Question(PostgresBase):
    """
    Question model for tracking user questions and AI responses.
    Stored in PostgreSQL.
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    similarity_score = Column(String(50), nullable=True)  # Store as string for flexibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="questions")

    def __repr__(self):
        return f"<Question(id={self.id}, question='{self.question_text[:50]}...')>"


class SearchLog(PostgresBase):
    """
    Search log model for analytics and improvement.
    Stored in PostgreSQL.
    """
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    results_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    search_type = Column(String(50), default="semantic")  # semantic, keyword, hybrid
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<SearchLog(id={self.id}, query='{self.query[:30]}...', results={self.results_count})>"