import json
from pathlib import Path
from typing import Protocol

from models import  NoteRead

class NoteRepository(Protocol):
    def list_notes(self)-> list[NoteRead]:
        ...
    #如果 notes.json 不存在：
    #返回空列表

    #如果 notes.json 存在：
    #打开文件
    #json.load 读成字典
    #取出里面的 notes 列表
    #把每个字典变成 NoteRead 对象
    #返回 NoteRead 列表
    def save_notes(self, notes: list[NoteRead]) -> None:
        ...

class JsonNoteRepository:
    def __init__(self,filename:str|Path) ->None:
        self.filename=Path(filename)
    def list_notes(self)->list[NoteRead]:
        if not self.filename.exists():
            return []
        with self.filename.open("r",encoding="utf-8") as file:
            payload=json.load(file)
        raw_notes=payload.get("notes",[])
        if not isinstance(raw_notes,list):
            raise ValueError("notes.json 里的 notes 必须是列表")
        return [NoteRead.model_validate(raw_note) for raw_note in raw_notes]

    def save_notes(self, notes: list[NoteRead]) -> None:
        """确保文件夹存在
把每个 NoteRead 对象转成字典
包装成 {"notes": [...]}
写入 notes.json"""
        self.filename.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "notes": [note.model_dump(mode="json") for note in notes]
        }

        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)