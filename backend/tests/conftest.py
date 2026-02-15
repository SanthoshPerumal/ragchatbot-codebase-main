import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_rag_system():
    """Create a mock RAGSystem with sensible defaults."""
    rag = MagicMock()
    rag.session_manager.create_session.return_value = "test-session-123"
    rag.query.return_value = (
        "This is a test answer about course materials.",
        [{"course": "Test Course", "lesson": "Lesson 1", "link": "http://example.com"}],
    )
    rag.get_course_analytics.return_value = {
        "total_courses": 3,
        "course_titles": ["Course A", "Course B", "Course C"],
    }
    return rag


@pytest.fixture
def test_app(mock_rag_system):
    """Create a FastAPI test app with mocked RAG system.

    This builds the API endpoints directly rather than importing from app.py,
    which mounts static files from a frontend directory that doesn't exist in
    the test environment.
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional

    app = FastAPI(title="Test Course Materials RAG System")

    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[dict]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    rag_system = mock_rag_system

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()
            answer, sources = rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


@pytest.fixture
def client(test_app):
    """Create a TestClient for synchronous API tests."""
    from fastapi.testclient import TestClient

    return TestClient(test_app)
