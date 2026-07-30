from src.web.app import create_app


def test_chat_api_contains_handoff_fields(monkeypatch):
    app = create_app()
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"question": "酒店早餐可以报销餐费吗"})
    assert response.status_code == 200
    data = response.get_json()
    assert "answer" in data
    assert "citations" in data
    assert "handoff_required" in data
    assert "handoff_reason" in data
    assert "intent" in data
