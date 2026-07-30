from scripts.travel_cli import format_reply


def test_cli_reply_shape():
    payload = {
        "answer": "结论：不可以",
        "citations": [
            {
                "source": "GC_TE_Policy_v202212.pdf",
                "doc_version": "v202212",
                "section_hint": "Meal",
                "page_hint": 6,
                "excerpt": "Not cover Breakfast",
            }
        ],
        "handoff_required": False,
        "handoff_reason": None,
    }
    rendered = format_reply(payload)
    assert "结论" in rendered
    assert "引用" in rendered
    assert "GC_TE_Policy_v202212.pdf" in rendered
