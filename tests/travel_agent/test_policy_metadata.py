from pathlib import Path

from src.knowledge.loader import load_documents


def test_policy_chunks_include_metadata(tmp_path: Path):
    sample = tmp_path / "GC_TE_Policy_v202212_test.txt"
    sample.write_text("Meal Not cover Breakfast page 6", encoding="utf-8")

    docs = load_documents(tmp_path)
    assert docs
    first = docs[0]
    assert first["doc_version"] == "v202212"
    assert first["section_hint"] == "Meal"
    assert first["page_hint"] == 6
