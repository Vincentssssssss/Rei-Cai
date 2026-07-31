from app.services.translator import parse_batch_json_robust


def test_parse_batch_json_robust_extracts_translations():
    raw = '{"translations":[{"text":"A"},{"text":"B"}]}'
    assert parse_batch_json_robust(raw, 2) == ["A", "B"]


def test_parse_batch_json_robust_handles_fenced_json():
    raw = "answer:\n```json\n{\"translations\":[{\"text\":\"X\"}]}\n```"
    assert parse_batch_json_robust(raw, 1) == ["X"]
