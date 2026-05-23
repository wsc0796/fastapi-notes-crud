# Notes CRUD API

A production-structured FastAPI project demonstrating clean architecture, layered design, and comprehensive testing.

## Features

- Create, read, update, delete notes
- Partial updates via PATCH
- Search notes by keyword
- Pagination (skip/limit)
- Input validation via Pydantic
- Full test coverage with TestClient

## Tech Stack

- **Python 3.12**
- **FastAPI** — modern async web framework
- **Pydantic v2** — data validation & settings
- **pytest** — unit & integration testing
- **JSON file storage** — zero external dependencies

## Architecture

```
main.py              →  HTTP routes (translation layer)
dependencies.py      →  DI wiring (factory)
service.py           →  Business logic
repository.py        →  Persistence (JSON file)
models.py            →  Data contracts (Pydantic)
```

Dependency direction: `main → service → repository` (no circular dependencies).

## Quick Start

```bash
# install dependencies
pip install fastapi uvicorn pytest

# start server
uvicorn main:app --reload

# open API docs
# http://localhost:8000/docs
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/notes` | Create a note |
| GET | `/notes` | List notes (paginated) |
| GET | `/notes/search?q=` | Search notes by keyword |
| GET | `/notes/{id}` | Get a single note |
| PATCH | `/notes/{id}` | Partially update a note |
| DELETE | `/notes/{id}` | Delete a note |

### Request Example

```json
POST /notes
{
  "content": "Learn FastAPI",
  "title": "Study Plan",
  "priority": 1,
  "category": "learning"
}
```

### Response Example

```json
{
  "id": 1,
  "content": "Learn FastAPI",
  "title": "Study Plan",
  "priority": 1,
  "category": "learning",
  "created_at": "2026-05-22T10:00:00"
}
```

## Testing

```bash
pytest test_notes_api.py -v
```

15 tests covering:
- CRUD happy paths
- 404 / 422 error handling
- Pagination
- Search with no match
- Partial update

## Project Status

Actively maintained as a learning portfolio project. Next iterations will add:
- Database integration (SQLite/PostgreSQL)
- User authentication
- Docker deployment
