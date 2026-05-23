"""
最小自检脚本。

不启动 uvicorn，直接用 TestClient 模拟 HTTP 请求，自动验证所有接口。
运行：
    python run_checks.py
"""

from fastapi.testclient import TestClient

import dependencies
from main import app


def main() -> None:
    # 需求①：清空旧数据，确保每次测试从干净状态开始
    if dependencies.DATA_FILE.exists():
        dependencies.DATA_FILE.unlink()

    # 需求②：创建测试客户端（模拟 HTTP 请求，不启动真实服务器）
    client = TestClient(app)

    # 需求③：测试根路由 —— 服务是否启动
    assert client.get("/").status_code == 200

    # 需求④：测试创建笔记 —— POST /notes
    created = client.post(
        "/notes",
        json={"content": "今天学习 FastAPI", "title": "FastAPI 学习记录", "priority": 3, "category": "学习"},
    )
    assert created.status_code == 201, created.text       # 创建成功
    note = created.json()                                  # 拿到响应 JSON
    note_id = note["id"]                                   # 记下 id 给后面用

    # 需求⑤：验证返回的数据 —— content 原样返回，created_at 自动生成
    assert note["content"] == "今天学习 FastAPI"
    assert note["title"] == "FastAPI 学习记录"
    assert "created_at" in note                            # 系统自动生成了时间戳

    # 需求⑥：测试查看全部 —— GET /notes
    listed = client.get("/notes")
    assert listed.status_code == 200
    assert len(listed.json()) == 1                         # 刚创建了 1 条

    # 需求⑦：测试查看单条 —— GET /notes/{id}
    single = client.get(f"/notes/{note_id}")
    assert single.status_code == 200
    assert single.json()["content"] == "今天学习 FastAPI"

    # 需求⑧：测试 404 错误 —— 查不存在的笔记应返回 404
    missing = client.get("/notes/999")
    assert missing.status_code == 404

    # 需求⑨：测试删除 —— DELETE /notes/{id}
    deleted = client.delete(f"/notes/{note_id}")
    assert deleted.status_code == 204                      # 删除成功，无返回内容

    # 需求⑩：确认删干净了 —— 再查列表应为空
    after_delete = client.get("/notes")
    assert len(after_delete.json()) == 0

    print("all checks passed")


if __name__ == "__main__":
    main()
