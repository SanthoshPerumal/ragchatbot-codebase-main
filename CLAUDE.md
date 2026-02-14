# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
# Install dependencies
uv sync

# Start the server (from project root)
./run.sh

# Or manually
cd backend && uv run uvicorn app:app --reload --port 8000
```

The app runs at http://localhost:8000. An `ANTHROPIC_API_KEY` must be set in a `.env` file at the project root.

**Always use `uv` to run commands — never use `pip` directly.** Use `uv run` to execute scripts and `uv sync` to install dependencies.

## Architecture

This is a RAG (Retrieval-Augmented Generation) chatbot for querying course materials. It uses an **agentic tool-calling pattern**: Claude decides whether to search the vector store via a tool call, rather than always retrieving context.

### Query Flow

1. **Frontend** (`frontend/script.js`) sends `POST /api/query` with `{ query, session_id }`
2. **FastAPI endpoint** (`backend/app.py`) delegates to `RAGSystem.query()`
3. **RAGSystem** (`backend/rag_system.py`) orchestrates: gets session history, calls `AIGenerator` with tool definitions
4. **AIGenerator** (`backend/ai_generator.py`) makes a Claude API call. If Claude returns `stop_reason: "tool_use"`, it executes the tool and makes a **second API call** with results (without tools, preventing loops)
5. **CourseSearchTool** (`backend/search_tools.py`) performs semantic search via `VectorStore`
6. **VectorStore** (`backend/vector_store.py`) queries ChromaDB with optional course/lesson filters. Course name resolution uses fuzzy vector matching against the `course_catalog` collection

### Key Design Decisions

- **Two ChromaDB collections**: `course_catalog` (course metadata for name resolution) and `course_content` (chunked text for semantic search)
- **Tool-based search**: Claude receives `search_course_content` as a tool and autonomously decides when/how to search, including choosing filters
- **Session history** is appended to the system prompt as plain text, not as structured messages
- **Sources tracking**: `CourseSearchTool` stores sources in `last_sources` after each search; `ToolManager` collects and resets them per query
- **Document deduplication**: On startup, courses already in ChromaDB are skipped (matched by title)

### Document Format

Course `.txt` files in `docs/` follow a specific structure with metadata headers (`Course Title:`, `Course Link:`, `Course Instructor:`) followed by lessons (`Lesson N: Title`). The `DocumentProcessor` parses this format.

## Configuration

All tunable parameters are in `backend/config.py`: chunk size (800), overlap (100), max results (5), max history (2), model name, embedding model. These are set as dataclass defaults, not env vars (except the API key).
