"""
组装车间：创建对象并将它们连接在一起。

依赖方向：repository → service → main
这个文件只负责"造"，不负责"用"。
"""

from pathlib import Path

from repository import JsonNoteRepository
from service import NoteService

# 需求①：找到 notes.json 文件，不写死路径（换了电脑也能跑）
# __file__ = 当前文件位置 → .with_name() = 同目录下的 notes.json
DATA_FILE = Path(__file__).with_name("notes.json")

# 需求②：造一个能读写 notes.json 的仓库对象
# 把文件路径告诉它，以后调 .list_notes() / .save_notes() 它就知道操作哪个文件
note_repository = JsonNoteRepository(DATA_FILE)

# 需求③：造一个业务层对象，把仓库塞进去
# NoteService 只依赖仓库的行为约定，不关心底层的实现
note_service = NoteService(note_repository)

# 需求④：给 FastAPI 留一个取货口（Depends() 需要一个可调用对象）
# 每次请求进来，FastAPI 调这个函数 → 拿到同一个 note_service 单例
def get_note_service() -> NoteService:
    return note_service
