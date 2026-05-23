from datetime import datetime

from models import NoteCreate, NoteRead, NoteUpdate
from repository import NoteRepository


class NoteNotFoundError(Exception):
    def __init__(self, note_id: int) -> None:
        self.note_id = note_id
        super().__init__(f"笔记 {note_id} 不存在")


class NoteService:
    def __init__(self, repository: NoteRepository) -> None:
        self.repository = repository

    def list_notes(self, skip: int = 0, limit: int = 10,category: str | None = None) -> list[NoteRead]:
        notes = self.repository.list_notes()
        if category is not None:
            notes = [note for note in notes if note.category == category]
        return notes[skip:skip + limit]
    

    def create_note(self, note_create: NoteCreate) -> NoteRead:
        notes = self.repository.list_notes()
        next_id = max((note.id for note in notes), default=0) + 1
        note = NoteRead(
            id=next_id,
            content=note_create.content,
            created_at=datetime.now(),
            title=note_create.title,
            priority=note_create.priority,
            category=note_create.category
        )
        notes.append(note)
        self.repository.save_notes(notes)
        return note

    def get_note(self, note_id: int) -> NoteRead:
        for note in self.repository.list_notes():
            if note.id == note_id:
                return note
        raise NoteNotFoundError(note_id)

    def delete_note(self, note_id: int) -> None:
        notes = self.repository.list_notes()
        remaining_notes = [note for note in notes if note.id != note_id]

        if len(remaining_notes) == len(notes):
            raise NoteNotFoundError(note_id)

        self.repository.save_notes(remaining_notes)

    def update_note(self, note_id: int, note_update: NoteUpdate) -> NoteRead:
        """更新笔记：只改传过来的字段，没传的保持不变"""
        notes = self.repository.list_notes()
        for i, note in enumerate(notes):
            if note.id == note_id:
                update_data = note_update.model_dump(exclude_unset=True)
                updated_note = note.model_copy(update=update_data)
                notes[i] = updated_note
                self.repository.save_notes(notes)
                return updated_note
        raise NoteNotFoundError(note_id)

    def search_notes(self, keyword: str) -> list[NoteRead]:
        """按关键词搜索笔记（不区分大小写）"""
        notes = self.repository.list_notes()
        return [
            note for note in notes
            if keyword.lower() in note.content.lower()
        ]
