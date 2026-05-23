"""
TestClient 测试模板。

每个接口的测试模式：
  1. test_<action>         → 正常情况（happy path）
  2. test_<action>_<edge>  → 边界情况（404 / 422 / 空结果）
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

SAMPLE_NOTE = {"content": "hello", "title": "t", "priority": 3, "category": "work"}


class TestNotesAPI:
    """笔记 API 测试"""

    # ──  helpers ──────────────────────────────────────────

    def _create_note(self, **overrides: str | int) -> dict:
        """创建一条笔记，返回 JSON 响应体。overrides 可覆盖默认字段"""
        payload = {**SAMPLE_NOTE, **overrides}
        resp = client.post("/notes", json=payload)
        assert resp.status_code == 201
        return resp.json()

    # ──  POST /notes  ─────────────────────────────────────

    def test_create_note(self):
        """正常创建 → 返回 201 + 完整笔记"""
        resp = client.post("/notes", json=SAMPLE_NOTE)
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "hello"
        assert data["title"] == "t"
        assert data["priority"] == 3
        assert data["category"] == "work"
        assert "id" in data
        assert "created_at" in data

    def test_create_note_empty_content(self):
        """content 为空 → 422"""
        resp = client.post("/notes", json={**SAMPLE_NOTE, "content": ""})
        assert resp.status_code == 422

    # ──  GET /notes  ──────────────────────────────────────

    def test_list_notes(self):
        """查看全部 → 返回列表"""
        resp = client.get("/notes")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_notes_pagination(self):
        """分页：?skip=0&limit=2 → 只返回 2 条"""
        for i in range(5):
            client.post("/notes", json=SAMPLE_NOTE)
        resp = client.get("/notes?skip=0&limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_notes_pagination_skip(self):
        """分页：?skip=2 → 跳过前 2 条"""
        resp = client.get("/notes?skip=2&limit=10")
        assert resp.status_code == 200

    def test_list_notes_filter_by_category(self):
        """?category=work → 只返回 category 为 work 的笔记"""
        self._create_note(category="work")
        self._create_note(category="personal")
        self._create_note(category="work")
        resp = client.get("/notes?category=work")
        assert resp.status_code == 200
        assert all(n["category"] == "work" for n in resp.json())

    def test_list_notes_filter_no_match(self):
        """过滤不存在 category → 空列表"""
        resp = client.get("/notes?category=non_existent")
        assert resp.status_code == 200
        assert resp.json() == []

    # ──  GET /notes/search?q=  ────────────────────────────

    def test_search_notes(self):
        """关键词匹配 → 返回过滤后的列表"""
        self._create_note(content="unique keyword for search")
        resp = client.get("/notes/search?q=unique")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_search_notes_no_match(self):
        """没有匹配 → 空列表"""
        resp = client.get("/notes/search?q=xxxxxxxxxx")
        assert resp.status_code == 200
        assert resp.json() == []

    # ──  GET /notes/{id}  ─────────────────────────────────

    def test_get_note(self):
        """存在 → 返回笔记"""
        note = self._create_note(content="get test")
        resp = client.get(f"/notes/{note['id']}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "get test"

    def test_get_note_not_found(self):
        """不存在 → 404"""
        resp = client.get("/notes/99999")
        assert resp.status_code == 404

    # ──  PATCH /notes/{id}  ───────────────────────────────

    def test_update_note(self):
        """只改 content → 只更新 content，其他字段不变"""
        note = self._create_note(content="old content", title="old title")
        resp = client.patch(f"/notes/{note['id']}", json={"content": "new content"})
        assert resp.status_code == 200
        assert resp.json()["content"] == "new content"
        assert resp.json()["title"] == "old title"

    def test_update_note_not_found(self):
        """不存在 → 404"""
        resp = client.patch("/notes/99999", json={"content": "x"})
        assert resp.status_code == 404

    # ──  DELETE /notes/{id}  ──────────────────────────────

    def test_delete_note(self):
        """存在 → 204"""
        note = self._create_note()
        resp = client.delete(f"/notes/{note['id']}")
        assert resp.status_code == 204

    def test_delete_note_not_found(self):
        """不存在 → 404"""
        resp = client.delete("/notes/99999")
        assert resp.status_code == 404
