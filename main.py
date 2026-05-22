"""FastAPI 入口：HTTP 路由层。"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from dependencies import get_note_service
from models import NoteCreate, NoteRead, NoteUpdate
from service import NoteNotFoundError, NoteService

app = FastAPI(title="Notes CRUD API")

NoteServiceDep = Annotated[NoteService, Depends(get_note_service)]


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Notes CRUD API is running"}


@app.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, service: NoteServiceDep) -> NoteRead:
    return service.create_note(note)


@app.get("/notes", response_model=list[NoteRead])
def list_notes(
    service: NoteServiceDep,
    skip: int = 0,
    limit: int = 10,
) -> list[NoteRead]:
    return service.list_notes(skip, limit)


@app.get("/notes/search", response_model=list[NoteRead])
def search_notes(q: str, service: NoteServiceDep) -> list[NoteRead]:
    return service.search_notes(q)


@app.get("/notes/{note_id}", response_model=NoteRead)
def get_note(note_id: int, service: NoteServiceDep) -> NoteRead:
    try:
        return service.get_note(note_id)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.patch("/notes/{note_id}", response_model=NoteRead)
def update_note(
    note_id: int, note_update: NoteUpdate, service: NoteServiceDep
) -> NoteRead:
    try:
        return service.update_note(note_id, note_update)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, service: NoteServiceDep) -> None:
    try:
        service.delete_note(note_id)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
