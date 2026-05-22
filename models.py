from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    content: str = Field(min_length=1)
    title: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    category: str = Field(min_length=1)

class NoteUpdate(BaseModel):
    """更新笔记：只传要改的字段，不传的字段保持不变（partial update）"""
    content: str | None = Field(default=None, min_length=1)
    title: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, min_length=1)
    priority: int | None = Field(default=None, ge=1, le=5)

class NoteRead(NoteCreate):
    id: int = Field(ge=1)
    created_at: datetime