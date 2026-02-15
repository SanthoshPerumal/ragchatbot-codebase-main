"""Tests for the FastAPI API endpoints."""

import pytest
from unittest.mock import MagicMock


class TestQueryEndpoint:
    """Tests for POST /api/query."""

    def test_query_with_session_id(self, client, mock_rag_system):
        response = client.post(
            "/api/query",
            json={"query": "What is machine learning?", "session_id": "existing-session"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "This is a test answer about course materials."
        assert data["session_id"] == "existing-session"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["course"] == "Test Course"

        mock_rag_system.query.assert_called_once_with(
            "What is machine learning?", "existing-session"
        )

    def test_query_without_session_id_creates_one(self, client, mock_rag_system):
        response = client.post(
            "/api/query",
            json={"query": "Tell me about Python"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_query_with_explicit_null_session_id(self, client, mock_rag_system):
        response = client.post(
            "/api/query",
            json={"query": "Hello", "session_id": None},
        )

        assert response.status_code == 200
        assert response.json()["session_id"] == "test-session-123"

    def test_query_returns_empty_sources(self, client, mock_rag_system):
        mock_rag_system.query.return_value = ("No results found.", [])

        response = client.post(
            "/api/query",
            json={"query": "Unknown topic", "session_id": "s1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sources"] == []
        assert data["answer"] == "No results found."

    def test_query_missing_query_field(self, client):
        response = client.post("/api/query", json={"session_id": "s1"})
        assert response.status_code == 422

    def test_query_empty_body(self, client):
        response = client.post("/api/query", json={})
        assert response.status_code == 422

    def test_query_rag_system_error_returns_500(self, client, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("Vector store unavailable")

        response = client.post(
            "/api/query",
            json={"query": "test", "session_id": "s1"},
        )

        assert response.status_code == 500
        assert "Vector store unavailable" in response.json()["detail"]


class TestCoursesEndpoint:
    """Tests for GET /api/courses."""

    def test_get_courses(self, client, mock_rag_system):
        response = client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 3
        assert data["course_titles"] == ["Course A", "Course B", "Course C"]

    def test_get_courses_empty(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": [],
        }

        response = client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_get_courses_error_returns_500(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("DB error")

        response = client.get("/api/courses")

        assert response.status_code == 500
        assert "DB error" in response.json()["detail"]


class TestResponseModels:
    """Tests for response schema validation."""

    def test_query_response_schema(self, client):
        response = client.post(
            "/api/query",
            json={"query": "test", "session_id": "s1"},
        )

        data = response.json()
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)

    def test_courses_response_schema(self, client):
        response = client.get("/api/courses")

        data = response.json()
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
