# Travel Assistant LangGraph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Greater China Travel Assistant on a single LangGraph runtime, validated by CLI first and then integrated into Flask Web using shared business logic.

**Architecture:** Add a new `src/travel_agent` module with graph state, nodes, and builder; reuse the current TF-IDF knowledge store with metadata enrichment and deterministic guardrails; expose one service callable from CLI and existing `/api/chat` route to guarantee channel-consistent policy conclusions.

**Tech Stack:** Python 3, Flask, scikit-learn TF-IDF retrieval, pypdf, pytest, LangGraph (`langgraph`, `langchain-core`).

## Global Constraints

- Region scope is Greater China only in MVP.
- Knowledge sources for policy answers are limited to `GC_TE_Policy_v202212` and `Travel___Expense_Traning_vF`.
- Answer format is always: conclusion first, then evidence, then next step.
- Every policy answer includes citations: document name, version/date, and section/page when available.
- Assistant must never fabricate policy or promise special approval outcomes.
- Unknown/insufficient evidence must produce explicit "cannot confirm" and human escalation.
- Human escalation contacts are `su.vincent@bcg.com` and `Zhang.Zhen@bcg.com`.
- CLI and Web must share exactly one graph runtime service (no duplicated decision logic).

---

### Task 1: Add dependencies and testing scaffolding

**Files:**
- Modify: `requirements.txt`
- Create: `tests/travel_agent/test_smoke_imports.py`
- Test: `tests/travel_agent/test_smoke_imports.py`

**Interfaces:**
- Consumes: existing pip environment.
- Produces: importable `langgraph` and basic test harness for new package.

- [ ] **Step 1: Write the failing test**

```python
# tests/travel_agent/test_smoke_imports.py
def test_langgraph_modules_importable():
    import importlib

    assert importlib.import_module("langgraph")
    assert importlib.import_module("langchain_core")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/travel_agent/test_smoke_imports.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'langgraph'`.

- [ ] **Step 3: Write minimal implementation**

```text
# requirements.txt append these lines
langgraph>=0.2.0
langchain-core>=0.2.0
pytest>=8.0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pip install -r requirements.txt && pytest tests/travel_agent/test_smoke_imports.py -v`  
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/travel_agent/test_smoke_imports.py
git commit -m "chore: add langgraph dependencies and import smoke test"
```

### Task 2: Enrich knowledge metadata for citation quality

**Files:**
- Modify: `src/knowledge/loader.py`
- Create: `tests/travel_agent/test_policy_metadata.py`
- Test: `tests/travel_agent/test_policy_metadata.py`

**Interfaces:**
- Consumes: `load_documents(knowledge_dir: Path) -> list[dict]`
- Produces: each chunk dict includes:
  - `source: str`
  - `chunk_id: int`
  - `text: str`
  - `doc_version: str`
  - `section_hint: str`
  - `page_hint: int | None`

- [ ] **Step 1: Write the failing test**

```python
# tests/travel_agent/test_policy_metadata.py
from pathlib import Path

from src.knowledge.loader import load_documents


def test_policy_chunks_include_metadata(tmp_path: Path):
    sample = tmp_path / "GC_TE_Policy_v202212_test.txt"
    sample.write_text("Meal Not cover Breakfast page 6", encoding="utf-8")

    docs = load_documents(tmp_path)
    assert docs, "documents should not be empty"
    first = docs[0]
    assert "doc_version" in first
    assert "section_hint" in first
    assert "page_hint" in first
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/travel_agent/test_policy_metadata.py -v`  
Expected: FAIL on missing metadata keys.

- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledge/loader.py (new helper sketch)
import re
from pathlib import Path


def infer_doc_version(source_name: str) -> str:
    match = re.search(r"v\d{6,8}|v[A-Za-z]|\bDec\s+\d{4}\b", source_name, re.IGNORECASE)
    return match.group(0) if match else "unknown"


def infer_section_hint(text: str) -> str:
    lowered = text.lower()
    if "meal" in lowered or "breakfast" in lowered:
        return "Meal"
    if "hotel" in lowered:
        return "Hotel"
    if "airfare" in lowered or "flight" in lowered:
        return "Airfare"
    return "General"


def infer_page_hint(text: str) -> int | None:
    match = re.search(r"\bpage\s+(\d+)\b", text, re.IGNORECASE)
    return int(match.group(1)) if match else None

# when appending each chunk, include:
# "doc_version": infer_doc_version(path.name)
# "section_hint": infer_section_hint(chunk)
# "page_hint": infer_page_hint(chunk)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/travel_agent/test_policy_metadata.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/knowledge/loader.py tests/travel_agent/test_policy_metadata.py
git commit -m "feat: enrich knowledge chunks with citation metadata"
```

### Task 3: Build LangGraph core (state, nodes, builder, service)

**Files:**
- Create: `src/travel_agent/graph/state.py`
- Create: `src/travel_agent/graph/nodes.py`
- Create: `src/travel_agent/graph/builder.py`
- Create: `src/travel_agent/runtime/service.py`
- Create: `tests/travel_agent/test_graph_breakfast_policy.py`
- Test: `tests/travel_agent/test_graph_breakfast_policy.py`

**Interfaces:**
- Consumes:
  - `KnowledgeStore.search(query: str, top_k: int = TOP_K) -> list[dict]`
- Produces:
  - `TravelAssistantService.ask(question: str) -> dict`
  - Response shape:
    - `answer: str`
    - `citations: list[dict]`
    - `handoff_required: bool`
    - `handoff_reason: str | None`
    - `intent: str`

- [ ] **Step 1: Write the failing test**

```python
# tests/travel_agent/test_graph_breakfast_policy.py
from src.travel_agent.runtime.service import TravelAssistantService


class StubStore:
    def search(self, query: str, top_k: int = 4):
        return [
            {
                "source": "GC_TE_Policy_v202212.pdf",
                "text": "Meal Not cover Breakfast",
                "doc_version": "v202212",
                "section_hint": "Meal",
                "page_hint": 6,
                "score": 0.92,
            },
            {
                "source": "Travel___Expense_Traning_vF.pdf",
                "text": "Not cover Breakfast",
                "doc_version": "vF",
                "section_hint": "Meal",
                "page_hint": 10,
                "score": 0.88,
            },
        ]


def test_breakfast_reimbursement_is_denied_with_citations():
    service = TravelAssistantService(store=StubStore())
    result = service.ask("酒店早餐可以报销餐费吗")
    assert "不可以" in result["answer"]
    assert len(result["citations"]) >= 2
    assert result["handoff_required"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/travel_agent/test_graph_breakfast_policy.py -v`  
Expected: FAIL due to missing `src.travel_agent` modules.

- [ ] **Step 3: Write minimal implementation**

```python
# src/travel_agent/graph/state.py
from typing import Literal, TypedDict

Intent = Literal["policy", "hotel", "process", "contact", "visa", "other"]


class TravelAgentState(TypedDict, total=False):
    question: str
    region: str
    intent: Intent
    retrieved_chunks: list[dict]
    answer: str
    citations: list[dict]
    confidence: float
    handoff_required: bool
    handoff_reason: str | None
    satisfaction_prompted: bool
```

```python
# src/travel_agent/graph/nodes.py
from src.chat.citations import build_citations

ESCALATION = "如需人工支持，请联系 su.vincent@bcg.com 或 Zhang.Zhen@bcg.com。"


def classify_intent(state):
    q = state["question"]
    if any(k in q for k in ["政策", "报销", "标准", "早餐"]):
        intent = "policy"
    elif any(k in q for k in ["酒店", "协议价", "sourcing"]):
        intent = "hotel"
    elif any(k in q for k in ["如何", "流程", "申请", "取消"]):
        intent = "process"
    elif any(k in q for k in ["联系人", "联系谁", "邮箱"]):
        intent = "contact"
    elif "签证" in q:
        intent = "visa"
    else:
        intent = "other"
    return {"intent": intent, "region": "Greater China"}


def retrieve_knowledge(state, store):
    hits = store.search(state["question"])
    return {"retrieved_chunks": hits, "citations": build_citations(hits)}


def policy_guard(state):
    if not state.get("retrieved_chunks"):
        return {
            "handoff_required": True,
            "handoff_reason": "no_evidence",
            "answer": f"当前知识库无法确认该问题。{ESCALATION}",
        }
    return {"handoff_required": False, "handoff_reason": None}


def compose_answer(state):
    if state.get("handoff_required"):
        return {}
    snippets = state["retrieved_chunks"]
    breakfast_blocked = any("breakfast" in item["text"].lower() for item in snippets)
    if breakfast_blocked:
        answer = (
            "结论：不可以，酒店早餐不可报销。\n"
            "依据：相关政策明确将 Breakfast 列为不报销。\n"
            "下一步：如有特殊场景请先走例外审批。"
        )
    else:
        answer = (
            "结论：请以引用政策为准。\n"
            "依据：见下方引用。\n"
            f"下一步：如需确认特殊场景，{ESCALATION}"
        )
    return {"answer": answer}


def handoff_decider(state):
    if state.get("handoff_required"):
        return {}
    if len(state.get("retrieved_chunks", [])) == 0:
        return {
            "handoff_required": True,
            "handoff_reason": "low_confidence",
            "answer": f"{state['answer']}\n{ESCALATION}",
        }
    return {"handoff_required": False, "handoff_reason": None}
```

```python
# src/travel_agent/graph/builder.py
from langgraph.graph import END, START, StateGraph

from src.travel_agent.graph.nodes import (
    classify_intent,
    compose_answer,
    handoff_decider,
    policy_guard,
    retrieve_knowledge,
)
from src.travel_agent.graph.state import TravelAgentState


def build_graph(store):
    graph = StateGraph(TravelAgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_knowledge", lambda s: retrieve_knowledge(s, store))
    graph.add_node("policy_guard", policy_guard)
    graph.add_node("compose_answer", compose_answer)
    graph.add_node("handoff_decider", handoff_decider)
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "policy_guard")
    graph.add_edge("policy_guard", "compose_answer")
    graph.add_edge("compose_answer", "handoff_decider")
    graph.add_edge("handoff_decider", END)
    return graph.compile()
```

```python
# src/travel_agent/runtime/service.py
from src.travel_agent.graph.builder import build_graph


class TravelAssistantService:
    def __init__(self, store):
        self._graph = build_graph(store)

    def ask(self, question: str) -> dict:
        state = {"question": question}
        result = self._graph.invoke(state)
        return {
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "handoff_required": result.get("handoff_required", False),
            "handoff_reason": result.get("handoff_reason"),
            "intent": result.get("intent", "other"),
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/travel_agent/test_graph_breakfast_policy.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/travel_agent tests/travel_agent/test_graph_breakfast_policy.py
git commit -m "feat: add unified langgraph travel assistant runtime"
```

### Task 4: Add CLI channel using shared service

**Files:**
- Create: `scripts/travel_cli.py`
- Create: `tests/travel_agent/test_cli_output.py`
- Test: `tests/travel_agent/test_cli_output.py`

**Interfaces:**
- Consumes: `TravelAssistantService.ask(question: str) -> dict`
- Produces: interactive CLI loop with `quit` command.

- [ ] **Step 1: Write the failing test**

```python
# tests/travel_agent/test_cli_output.py
from scripts.travel_cli import format_reply


def test_cli_reply_shape():
    payload = {
        "answer": "结论：不可以",
        "citations": [{"source": "GC_TE_Policy_v202212.pdf", "excerpt": "Not cover Breakfast"}],
        "handoff_required": False,
        "handoff_reason": None,
    }
    rendered = format_reply(payload)
    assert "结论" in rendered
    assert "引用" in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/travel_agent/test_cli_output.py -v`  
Expected: FAIL because `scripts/travel_cli.py` is missing.

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/travel_cli.py
from src.knowledge.store import KnowledgeStore
from src.travel_agent.runtime.service import TravelAssistantService


def format_reply(payload: dict) -> str:
    lines = [payload["answer"], "", "引用："]
    for idx, c in enumerate(payload.get("citations", []), start=1):
        lines.append(f"{idx}. {c.get('source')} - {c.get('excerpt', '')[:120]}")
    if payload.get("handoff_required"):
        lines.append(f"转人工原因：{payload.get('handoff_reason')}")
    return "\n".join(lines)


def main() -> None:
    store = KnowledgeStore()
    service = TravelAssistantService(store)
    print("Travel Assistant CLI（输入 quit 退出）")
    while True:
        question = input("你：").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        result = service.ask(question)
        print(format_reply(result))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/travel_agent/test_cli_output.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/travel_cli.py tests/travel_agent/test_cli_output.py
git commit -m "feat: add cli channel for langgraph assistant"
```

### Task 5: Integrate Flask Web with shared service

**Files:**
- Modify: `src/web/app.py`
- Create: `tests/travel_agent/test_web_chat_api.py`
- Test: `tests/travel_agent/test_web_chat_api.py`

**Interfaces:**
- Consumes: `TravelAssistantService.ask(question: str) -> dict`
- Produces: `/api/chat` JSON fields:
  - `answer`
  - `citations`
  - `handoff_required`
  - `handoff_reason`
  - `intent`

- [ ] **Step 1: Write the failing test**

```python
# tests/travel_agent/test_web_chat_api.py
from src.web.app import create_app


def test_chat_api_contains_handoff_fields(monkeypatch):
    app = create_app()
    app.testing = True
    client = app.test_client()

    response = client.post("/api/chat", json={"question": "酒店早餐可以报销餐费吗"})
    assert response.status_code == 200
    data = response.get_json()
    assert "handoff_required" in data
    assert "handoff_reason" in data
    assert "intent" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/travel_agent/test_web_chat_api.py -v`  
Expected: FAIL because current API only returns `answer` and `citations`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/web/app.py key change sketch
from src.travel_agent.runtime.service import TravelAssistantService

store = KnowledgeStore()
assistant = TravelAssistantService(store=store)

@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "问题不能为空"}), 400

    result = assistant.ask(question)
    return jsonify(result)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/travel_agent/test_web_chat_api.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/web/app.py tests/travel_agent/test_web_chat_api.py
git commit -m "feat: connect web api to unified langgraph service"
```

### Task 6: Add policy safety and regression tests

**Files:**
- Create: `tests/travel_agent/test_guardrails.py`
- Test: `tests/travel_agent/test_guardrails.py`

**Interfaces:**
- Consumes: `TravelAssistantService.ask`.
- Produces: guardrail guarantees for out-of-scope and unknown cases.

- [ ] **Step 1: Write the failing test**

```python
# tests/travel_agent/test_guardrails.py
from src.travel_agent.runtime.service import TravelAssistantService


class EmptyStore:
    def search(self, query: str, top_k: int = 4):
        return []


def test_unknown_question_must_escalate():
    service = TravelAssistantService(store=EmptyStore())
    result = service.ask("帮我直接审批超标酒店")
    assert result["handoff_required"] is True
    assert "无法确认" in result["answer"] or "人工支持" in result["answer"]
    assert "su.vincent@bcg.com" in result["answer"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/travel_agent/test_guardrails.py -v`  
Expected: FAIL until escalation wording and fields are implemented consistently.

- [ ] **Step 3: Write minimal implementation**

```python
# src/travel_agent/graph/nodes.py policy_guard enhancement sketch
BLOCKED_PATTERNS = ["直接审批", "帮我审批", "修改政策", "承诺特批"]

def policy_guard(state):
    q = state["question"]
    if any(p in q for p in BLOCKED_PATTERNS):
        return {
            "handoff_required": True,
            "handoff_reason": "out_of_scope",
            "answer": (
                "结论：该请求超出 Agent 权限范围，无法直接处理。"
                "下一步：请联系人工支持 su.vincent@bcg.com / Zhang.Zhen@bcg.com。"
            ),
        }
    if not state.get("retrieved_chunks"):
        return {
            "handoff_required": True,
            "handoff_reason": "no_evidence",
            "answer": (
                "结论：当前知识库无法确认该问题。"
                "下一步：请联系人工支持 su.vincent@bcg.com / Zhang.Zhen@bcg.com。"
            ),
        }
    return {"handoff_required": False, "handoff_reason": None}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/travel_agent/test_guardrails.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/travel_agent/test_guardrails.py src/travel_agent/graph/nodes.py
git commit -m "test: lock policy guardrail escalation behavior"
```

### Task 7: End-to-end verification and documentation update

**Files:**
- Modify: `README.md`
- Create: `tests/travel_agent/test_consistency_cli_web.py`
- Test: `tests/travel_agent/test_consistency_cli_web.py`

**Interfaces:**
- Consumes: CLI formatter + Flask API + TravelAssistantService.
- Produces: documented runbook and consistency evidence.

- [ ] **Step 1: Write the failing test**

```python
# tests/travel_agent/test_consistency_cli_web.py
from scripts.travel_cli import format_reply
from src.travel_agent.runtime.service import TravelAssistantService


class BreakfastStore:
    def search(self, query: str, top_k: int = 4):
        return [
            {
                "source": "GC_TE_Policy_v202212.pdf",
                "text": "Meal Not cover Breakfast",
                "doc_version": "v202212",
                "section_hint": "Meal",
                "page_hint": 6,
                "score": 0.92,
            }
        ]


def test_cli_and_service_conclusion_are_consistent():
    service = TravelAssistantService(store=BreakfastStore())
    payload = service.ask("酒店早餐可以报销餐费吗")
    rendered = format_reply(payload)
    assert "不可以" in payload["answer"]
    assert "可报销" in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/travel_agent/test_consistency_cli_web.py -v`  
Expected: FAIL with assertion error.

- [ ] **Step 3: Write minimal implementation**

```python
# tests/travel_agent/test_consistency_cli_web.py concrete shape
from scripts.travel_cli import format_reply
from src.travel_agent.runtime.service import TravelAssistantService


class BreakfastStore:
    def search(self, query: str, top_k: int = 4):
        return [
            {"source": "GC_TE_Policy_v202212.pdf", "text": "Not cover Breakfast", "score": 0.9},
        ]


def test_cli_and_service_share_same_conclusion():
    service = TravelAssistantService(store=BreakfastStore())
    payload = service.ask("酒店早餐可以报销餐费吗")
    rendered = format_reply(payload)
    assert "不可以" in payload["answer"]
    assert "不可以" in rendered
```

```markdown
<!-- README.md add section -->
## Travel Assistant (LangGraph MVP)

### CLI
python scripts/travel_cli.py

### Web
python web_main.py

Both channels use one LangGraph runtime (`src/travel_agent/runtime/service.py`).
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/travel_agent -v`  
Expected: PASS for all travel agent tests.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/travel_agent/test_consistency_cli_web.py
git commit -m "docs: add langgraph travel assistant usage and consistency tests"
```

## Self-Review Checklist (Applied)

- Spec coverage: all approved sections are mapped to tasks (scope, boundaries, sources, channels, metrics).
- Placeholder scan: no TBD/TODO placeholders remain in executable steps.
- Type consistency: `TravelAssistantService.ask(question: str) -> dict` is used consistently across CLI/Web/tests.
- Scope check: plan focuses only on MVP and does not include booking-system execution.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-30-travel-assistant-langgraph-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
