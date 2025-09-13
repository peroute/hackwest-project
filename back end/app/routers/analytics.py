"""
Analytics endpoints for search logs and usage statistics.
Provides insights into user behavior and search patterns.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..database import get_postgres_db
from ..models import SearchLog, User, Question
from ..schemas import SearchLog as SearchLogSchema

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/search-log", response_model=SearchLogSchema)
async def create_search_log(
    search_log: SearchLogSchema,
    db: Session = Depends(get_postgres_db)
):
    """
    Create a new search log entry.
    """
    db_log = SearchLog(
        query=search_log.query,
        results_count=search_log.results_count,
        user_id=search_log.user_id,
        search_type=search_log.search_type,
        response_time_ms=search_log.response_time_ms
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


@router.get("/search-stats")
async def get_search_statistics(
    days: int = 7,
    db: Session = Depends(get_postgres_db)
):
    """
    Get search statistics for the last N days.
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # Total searches
    total_searches = db.query(SearchLog).filter(
        SearchLog.created_at >= start_date
    ).count()
    
    # Average response time
    avg_response_time = db.query(func.avg(SearchLog.response_time_ms)).filter(
        SearchLog.created_at >= start_date,
        SearchLog.response_time_ms.isnot(None)
    ).scalar() or 0
    
    # Search types distribution
    search_types = db.query(
        SearchLog.search_type,
        func.count(SearchLog.id).label('count')
    ).filter(
        SearchLog.created_at >= start_date
    ).group_by(SearchLog.search_type).all()
    
    # Top queries
    top_queries = db.query(
        SearchLog.query,
        func.count(SearchLog.id).label('count')
    ).filter(
        SearchLog.created_at >= start_date
    ).group_by(SearchLog.query).order_by(desc('count')).limit(10).all()
    
    # User activity
    active_users = db.query(func.count(func.distinct(SearchLog.user_id))).filter(
        SearchLog.created_at >= start_date,
        SearchLog.user_id.isnot(None)
    ).scalar() or 0
    
    return {
        "period_days": days,
        "total_searches": total_searches,
        "average_response_time_ms": round(avg_response_time, 2),
        "active_users": active_users,
        "search_types": [
            {"type": st[0], "count": st[1]} for st in search_types
        ],
        "top_queries": [
            {"query": tq[0], "count": tq[1]} for tq in top_queries
        ]
    }


@router.get("/user-activity/{user_id}")
async def get_user_activity(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_postgres_db)
):
    """
    Get activity statistics for a specific user.
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # User searches
    user_searches = db.query(SearchLog).filter(
        SearchLog.user_id == user_id,
        SearchLog.created_at >= start_date
    ).count()
    
    # User questions
    user_questions = db.query(Question).filter(
        Question.user_id == user_id,
        Question.created_at >= start_date
    ).count()
    
    # User resources (now stored in MongoDB Atlas - not available in PostgreSQL)
    user_resources = 0  # Resources are now stored in MongoDB Atlas only
    
    # Recent activity
    recent_searches = db.query(SearchLog).filter(
        SearchLog.user_id == user_id,
        SearchLog.created_at >= start_date
    ).order_by(desc(SearchLog.created_at)).limit(10).all()
    
    return {
        "user_id": user_id,
        "period_days": days,
        "searches": user_searches,
        "questions": user_questions,
        "resources_created": user_resources,
        "recent_searches": [
            {
                "query": search.query,
                "search_type": search.search_type,
                "results_count": search.results_count,
                "created_at": search.created_at.isoformat()
            }
            for search in recent_searches
        ]
    }


@router.get("/system-health")
async def get_system_health(db: Session = Depends(get_postgres_db)):
    """
    Get system health metrics.
    """
    # Database statistics
    total_users = db.query(User).count()
    total_resources = 0  # Resources are now stored in MongoDB Atlas only
    total_questions = db.query(Question).count()
    total_search_logs = db.query(SearchLog).count()
    
    # Recent activity (last 24 hours)
    recent_activity = db.query(SearchLog).filter(
        SearchLog.created_at >= datetime.now() - timedelta(hours=24)
    ).count()
    
    # Vector database status
    from ..gemini import get_vector_database_status
    vector_status = get_vector_database_status()
    
    return {
        "database_stats": {
            "total_users": total_users,
            "total_resources": total_resources,
            "total_questions": total_questions,
            "total_search_logs": total_search_logs,
            "recent_activity_24h": recent_activity
        },
        "vector_database": vector_status,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/search-trends")
async def get_search_trends(
    days: int = 30,
    db: Session = Depends(get_postgres_db)
):
    """
    Get search trends over time.
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # Daily search counts
    daily_searches = db.query(
        func.date(SearchLog.created_at).label('date'),
        func.count(SearchLog.id).label('count')
    ).filter(
        SearchLog.created_at >= start_date
    ).group_by(
        func.date(SearchLog.created_at)
    ).order_by('date').all()
    
    # Search type trends
    search_type_trends = db.query(
        func.date(SearchLog.created_at).label('date'),
        SearchLog.search_type,
        func.count(SearchLog.id).label('count')
    ).filter(
        SearchLog.created_at >= start_date
    ).group_by(
        func.date(SearchLog.created_at),
        SearchLog.search_type
    ).order_by('date').all()
    
    return {
        "period_days": days,
        "daily_searches": [
            {"date": str(ds[0]), "count": ds[1]} for ds in daily_searches
        ],
        "search_type_trends": [
            {
                "date": str(stt[0]),
                "search_type": stt[1],
                "count": stt[2]
            }
            for stt in search_type_trends
        ]
    }
