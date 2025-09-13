"""
AI-powered Q&A endpoints with vector similarity search.
Integrates Gemini AI with Qdrant vector database for intelligent responses.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_postgres_db
from ..schemas import AskRequest, AskResponse, SearchLogCreate
from ..gemini import ask_question_with_ai
from ..models import SearchLog, Question
import time

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("/", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    db: Session = Depends(get_postgres_db)
):
    """
    Ask a question and get an AI-generated answer using vector similarity search.
    """
    start_time = time.time()
    
    try:
        # Get AI response with vector search
        response = await ask_question_with_ai(
            question=request.question,
            user_id=request.user_id,
            search_type=request.search_type
        )
        
        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)
        
        # Log the search
        search_log = SearchLog(
            query=request.question,
            results_count=len(response.relevant_resources),
            user_id=request.user_id,
            search_type=request.search_type,
            response_time_ms=response_time
        )
        db.add(search_log)
        
        # Log the question
        question = Question(
            question_text=request.question,
            answer_text=response.answer,
            user_id=request.user_id,
            similarity_score=str(response.relevant_resources[0].similarity_score) if response.relevant_resources else None
        )
        db.add(question)
        
        db.commit()
        
        return response
        
    except Exception as e:
        # Log failed search
        search_log = SearchLog(
            query=request.question,
            results_count=0,
            user_id=request.user_id,
            search_type=request.search_type,
            response_time_ms=int((time.time() - start_time) * 1000)
        )
        db.add(search_log)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/history/{user_id}")
async def get_question_history(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_postgres_db)
):
    """
    Get question history for a specific user.
    """
    questions = db.query(Question).filter(
        Question.user_id == user_id
    ).order_by(Question.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": q.id,
            "question": q.question_text,
            "answer": q.answer_text,
            "similarity_score": q.similarity_score,
            "created_at": q.created_at.isoformat()
        }
        for q in questions
    ]


@router.get("/stats/overview")
async def get_qa_stats(db: Session = Depends(get_postgres_db)):
    """
    Get Q&A statistics overview.
    """
    total_questions = db.query(Question).count()
    total_searches = db.query(SearchLog).count()
    
    # Average response time
    avg_response_time = db.query(
        db.func.avg(SearchLog.response_time_ms)
    ).filter(
        SearchLog.response_time_ms.isnot(None)
    ).scalar() or 0
    
    # Recent activity (last 24 hours)
    from datetime import datetime, timedelta
    recent_questions = db.query(Question).filter(
        Question.created_at >= datetime.now() - timedelta(hours=24)
    ).count()
    
    return {
        "total_questions": total_questions,
        "total_searches": total_searches,
        "average_response_time_ms": round(avg_response_time, 2),
        "recent_questions_24h": recent_questions
    }