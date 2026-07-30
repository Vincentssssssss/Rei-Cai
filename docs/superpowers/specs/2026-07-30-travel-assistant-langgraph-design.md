# Travel Assistant (Greater China) LangGraph Design

## 1. Background and Objective

The internal Travel Assistant serves as a single conversational entry point for Greater China employees to quickly get accurate travel-related answers. It is designed to reduce repetitive manual responses from Travel Team while keeping policy consistency and auditability.

Primary objectives:
- Provide clear, accurate, and up-to-date travel information.
- Return actionable next steps for process questions.
- Route out-of-scope or uncertain cases to human support.
- Enforce strict non-hallucination and business-boundary controls.

## 2. Scope

### 2.1 In Scope (MVP)
- Travel policy lookup (hotel, meal, airfare, reimbursement, approvals).
- Hotel resource lookup (contract hotel guidance and sourcing path).
- Process guidance (how to apply/cancel/request support).
- Contact lookup (Travel/Finance/Visa support routing).
- Visa and common travel guidance strictly based on approved knowledge.

### 2.2 Regional Coverage
- Greater China only for MVP.

### 2.3 Human Escalation
- `su.vincent@bcg.com`
- `Zhang.Zhen@bcg.com`

## 3. Knowledge Sources and Grounding Rules

The assistant must prioritize only official documents:
- `GC_TE_Policy_v202212` (Global Travel & Entertainment Policy, Greater China, Dec 2022).
- `Travel___Expense_Traning_vF` (Travel & Expense Training for Greater China).

Grounding requirements for every policy answer:
- Include source document name.
- Include version/date.
- Include section and page number where possible.
- If insufficient evidence exists, explicitly say "cannot confirm" and route to human support.

## 4. Business Boundary (Hard Constraints)

The assistant can:
- Explain official travel policy and standard process.
- Provide next-step guidance.
- Route to correct owners/teams when needed.

The assistant cannot:
- Make final approvals for employees.
- Modify policy content.
- Decide special-case outcomes.
- Replace Travel Team decision-making.
- Provide recommendations without policy basis.
- Execute booking/changes/expense operations on behalf of users.

## 5. Solution Approach

Use **one unified LangGraph** for all channels.

Why this approach:
- One source of business logic across CLI and Web.
- Lower maintenance risk than separate graphs.
- Consistent boundary enforcement and citation structure.

## 6. Architecture

1. **Knowledge Layer**
   - Parse the two approved PDFs.
   - Chunk and index with metadata:
     - `document_name`
     - `version`
     - `section`
     - `page`
     - `region` (Greater China)

2. **LangGraph Core**
   - Intent classification.
   - Context retrieval.
   - Policy guardrail check.
   - Answer composition.
   - Handoff decision.
   - Satisfaction prompt.

3. **Channel Layer**
   - CLI channel for fast validation.
   - Existing Flask Web chat channel for pilot use.
   - Both consume the same graph runtime service.

4. **Ops Layer**
   - Logging of intent and handoff reason.
   - Feedback capture (resolved/not resolved + satisfaction).

## 7. Graph State and Nodes

### 7.1 State Schema
- `question`: original user question.
- `region`: default `Greater China`.
- `intent`: `policy|hotel|process|contact|visa|other`.
- `retrieved_chunks`: grounded evidence with metadata.
- `answer`: final response text.
- `citations`: normalized citations list.
- `confidence`: confidence signal for routing.
- `handoff_required`: boolean.
- `handoff_reason`: `no_evidence|conflict|out_of_scope|low_confidence`.
- `satisfaction_prompted`: boolean.

### 7.2 Nodes
1. `classify_intent`
2. `retrieve_knowledge`
3. `policy_guard`
4. `compose_answer`
5. `handoff_decider`
6. `collect_feedback`
7. `end`

### 7.3 Standard Answer Shape
All answers should follow:
1. Conclusion first.
2. Evidence and citation.
3. Next step guidance.

If unknown:
1. Explicitly state cannot confirm.
2. Explain evidence gap briefly.
3. Route to support mailbox.

## 8. Example Policy QA (Grounded)

Question: "Can hotel breakfast be reimbursed as meal expense?"

Expected answer:
- Conclusion: No, breakfast is not reimbursable.
- Evidence:
  - `GC_TE_Policy_v202212`, Meal section, "Not cover: Breakfast" (page 6 in extracted PDF text sequence).
  - `Travel___Expense_Traning_vF`, Meals section, "Not cover: Breakfast" (slides around pages 9-10 in extracted PDF text sequence).
- Next step: For exceptions, request formal approval path; if unclear, contact `su.vincent@bcg.com` or `Zhang.Zhen@bcg.com`.

## 9. Delivery Plan (Option C)

Phase 1 (validation):
- Build CLI entrypoint first to validate graph behavior quickly.

Phase 2 (pilot-ready):
- Integrate existing Flask Web chat with the same runtime service.

Consistency rule:
- Same question must return same policy conclusion in CLI and Web.
- Display format can differ by channel, business result cannot.

## 10. Acceptance and Metrics

### 10.1 Functional Acceptance
- Policy questions return grounded answers with citations.
- Process questions include clear next steps.
- Contact questions return proper support channels.
- Out-of-knowledge questions are safely declined and escalated.
- Boundary-prohibited asks are rejected with policy-safe response.

### 10.2 Quality Metrics
- First Contact Resolution (FCR).
- Citation completeness rate.
- Rejection correctness rate (unknown handled correctly).
- Hallucination rate (knowledge-inconsistent outputs).
- Human handoff rate and handoff reason distribution.
- User satisfaction score.

### 10.3 Pre-Pilot Gate
- High-frequency QA set passes agreed threshold.
- Citation completeness meets agreed threshold.
- Zero critical policy-misguidance findings.
- Handoff workflow is operational with summary context.
