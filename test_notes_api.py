"""
TestClient 测试：覆盖 6 个接口 + 边界情况。

运行方式：
    pytest test_notes_api.py -v

或者：
    python -m pytest test_notes_api.py -v
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestNotesAPI:
    """笔记 API 测试"""

    def test_create_note(self):
        """创建笔记：传 content + title → 返回 201 + 笔记对象"""
        response = client.post("/notes", json={"content": "test note", "title": "test title", "priority": 3, "category": "work"})
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "test note"
        assert data["title"] == "test title"
        assert "id" in data
        assert "created_at" in data

    def test_create_note_empty_content(self):
        """创建笔记：传空字符串 → 返回 422"""
        response = client.post("/notes", json={"content": "", "title": "x", "priority": 3, "category": "work"})
        assert response.status_code == 422

    def test_list_notes(self):
        """查看全部：返回列表"""
        response = client.get("/notes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_notes_pagination(self):
        """/notes?skip=0&limit=2 → 只返回 2 条"""
        for i in range(5):
            client.post("/notes", json={"content": f"page test {i}", "title": f"t{i}", "priority": 3, "category": "work"})

        response = client.get("/notes?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_notes_pagination_skip(self):
        """/notes?skip=2 → 跳过前 2 条"""
        response = client.get("/notes?skip=2&limit=10")
        assert response.status_code == 200

    def test_search_notes(self):
        """搜索笔记：关键词匹配 → 返回过滤后的列表"""
        client.post("/notes", json={"content": "search test", "title": "s", "priority": 3, "category": "work"})
        response = client.get("/notes/search?q=search")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_search_notes_no_match(self):
        """搜索笔记：没有匹配 → 返回空列表"""
        response = client.get("/notes/search?q=xxxxxxxxxx")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_note(self):
        """查看单条：存在 → 返回笔记"""
        create_resp = client.post("/notes", json={"content": "get test", "title": "g", "priority": 3, "category": "work"})
        note_id = create_resp.json()["id"]

        response = client.get(f"/notes/{note_id}")
        assert response.status_code == 200
        assert response.json()["content"] == "get test"

    def test_get_note_not_found(self):
        """查看单条：不存在 → 返回 404"""
        response = client.get("/notes/99999")
        assert response.status_code == 404

    def test_update_note(self):
        """更新笔记：只改 content → 返回更新后的笔记"""
        create_resp = client.post("/notes", json={"content": "old content", "title": "old title", "priority": 3, "category": "work"})
        note_id = create_resp.json()["id"]

        response = client.patch(f"/notes/{note_id}", json={"content": "new content"})
        assert response.status_code == 200
        assert response.json()["content"] == "new content"
        assert response.json()["title"] == "old title"  # title 没传，保持不变

    def test_update_note_not_found(self):
        """更新笔记：不存在 → 返回 404"""
        response = client.patch("/notes/99999", json={"content": "x"})
        assert response.status_code == 404

    def test_delete_note(self):
        """删除笔记：存在 → 返回 204"""
        create_resp = client.post("/notes", json={"content": "delete me", "title": "d", "priority": 3, "category": "work"})
        note_id = create_resp.json()["id"]

        response = client.delete(f"/notes/{note_id}")
        assert response.status_code == 204

    def test_delete_note_not_found(self):
        """删除笔记：不存在 → 返回 404"""
        response = client.delete("/notes/99999")
        assert response.status_code == 404
