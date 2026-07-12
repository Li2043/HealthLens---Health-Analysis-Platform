# HealthLens — Safe AI Healthcare Consultation Workflow Demo

> **Positioning statement**
> HealthLens explores how LLM systems can support *safer* healthcare consultation
> experiences through structured workflow design, medical safety strategies, and
> risk-aware response generation.

> **Scope disclaimer**
> HealthLens is a product-design and engineering prototype. It is **not** a medical
> device, **not** medical advice, and **must not** be used for diagnosis, treatment,
> or clinical decision-making.

---

## 1. Problem Statement

Health-related user queries behave differently from ordinary information requests.
When someone types *"my chest feels tight and I'm short of breath"* into a chat box,
the interaction is simultaneously:

- **Uncertain** — the user rarely knows what is relevant. They report sensations,
  not structured clinical signals, and they often omit the detail that matters most.
- **Anxiety-driven** — the user is frequently worried, and the *emotional* goal
  ("tell me I'm okay") can conflict with the *safe* goal ("get this checked").
- **Risk-sensitive** — the cost of a wrong answer is asymmetric. A falsely
  reassuring response to a serious symptom is far more harmful than an overly
  cautious one.
- **Safety critical** — at the extreme, the right product behaviour is to stop
  giving information and tell the user to seek urgent in-person care.

A generic, general-purpose LLM chat system is poorly matched to these properties.
Left unconstrained, it tends to fail in predictable and dangerous ways:

| Failure mode | What it looks like | Why it is harmful |
| --- | --- | --- |
| **Unsafe advice** | Suggests a medication or a dose | Users may act on it without clinical oversight |
| **Overconfidence** | "This is almost certainly just stress" | Manufactures false reassurance, suppresses escalation |
| **Hallucinated diagnosis** | "You have hypertension" | Asserts a clinical conclusion the model cannot support |
| **Poor escalation decisions** | Treats chest pain like a sleep question | Misses the one situation where speed matters most |

The core problem is **not** that LLMs cannot produce fluent health text — they
clearly can. The problem is that fluency without structure, guardrails, and
escalation logic produces output that is *confidently wrong in exactly the
situations where being wrong is least acceptable.*

**HealthLens exists to explore safer consultation workflows around this problem.**

---

## 2. Product Goal

HealthLens designs and demonstrates an AI healthcare *consultation workflow* —
not a single model call — that improves interaction quality along five dimensions:

1. **Symptom understanding** — turn messy free text into structured, inspectable
   signals (vitals, mood, sleep, symptoms) with explicit confidence and evidence,
   instead of letting the model silently guess.
2. **Risk communication** — express risk in a calibrated, plain-language way that
   neither minimises nor catastrophises, and that always carries a "this is not a
   diagnosis" framing.
3. **Safe explanation generation** — constrain the LLM so its explanation is
   grounded in the structured signals and the deterministic risk result, with no
   diagnosis and no medication dosing.
4. **Escalation logic** — make the decision *"should this person be told to seek
   professional or urgent care?"* an explicit, designed step rather than an
   accident of phrasing.
5. **Healthcare interaction quality** — keep the user calm and informed while
   steering them toward the safe next action, and make the whole reasoning chain
   auditable for a reviewer.

A concrete way to read this goal: **HealthLens treats the LLM as one component
inside a safety-managed workflow, not as the product itself.**

---

## 3. Product Scope

Being explicit about scope is itself a safety strategy. It prevents scope creep
toward functionality the system is not qualified to provide.

### HealthLens is NOT

- a **diagnosis tool** — it never asserts that a user has a condition;
- a **treatment recommendation engine** — it never prescribes medication, doses,
  or therapies;
- a **triage replacement** — it does not replace clinical judgement, a clinician,
  or an emergency service.

### HealthLens IS

- a **healthcare consultation workflow prototype** — a structured,
  multi-stage pipeline (extraction → risk assessment → safety validation →
  explanation → escalation) that models how a safer consultation experience could
  be built;
- a **risk-aware AI interaction demo** — a working app where response behaviour
  changes with assessed risk level and where guardrails are enforced in code;
- a **medical safety design exploration** — a documented, layered safety policy
  (scope detection, unsafe-advice prevention, risk-aware design, emergency
  escalation, human referral) with honest discussion of benefits and limitations.

---

## 4. How the Positioning Maps to the Existing System

This repositioning is **incremental**, not a rewrite. The current codebase already
implements most of the workflow; the repositioning reframes it and names the gaps.

| Positioning concept | Where it lives today | Status |
| --- | --- | --- |
| Symptom signal extraction | `app/extractor.py`, `app/extraction_validator.py` | Built (mock + OpenAI providers) |
| Risk assessment | `app/risk_rules.py` (deterministic rules) | Built |
| Safety validation | `app/safety_validator.py` | Built (disclaimer + diagnosis/medication checks) |
| Explanation generation | `app/llm_service.py` (constrained system prompt) | Built (mock + OpenAI) |
| Escalation recommendation | `app/escalation.py` (red-flag detector + escalation levels) | Built — symptom-driven emergency detection overrides risk level |
| Workflow trace / auditability | `app/evaluation/runner.py` (`workflow_trace`) | Built for evaluation |
| Evaluation of safe behaviour | `app/evaluation/`, `tests/` | Built (curated cases + metrics) |

> **Honest gap note:** In the current implementation, safety validation runs
> *after* explanation generation as an output check. The target workflow in
> `CONSULTATION_WORKFLOW.md` describes safety validation as a stage that both
> gates explanation inputs and verifies explanation outputs. Closing that gap is
> a tracked design improvement, not a claim of current behaviour.

---

## 5. Why This Matters for a Healthcare AI Product Role

HealthLens is designed to demonstrate, in a single artifact, the competencies a
strategy-leaning healthcare AI product role requires:

- **AI healthcare workflow design** — a defined, staged consultation pipeline.
- **Product thinking** — clear problem framing, scope boundaries, and user
  scenarios with product implications (`USER_SCENARIOS.md`).
- **Medical safety strategy** — a layered safety policy with rationale,
  benefits, and limitations (`MEDICAL_AI_SAFETY_POLICY.md`).
- **User understanding** — scenarios grounded in real user motivation and pain.
- **Business scenario thinking** — positioning that names what the product is and
  is not, so it could plug into a larger consumer-health offering responsibly.
- **AI application building capability** — a working FastAPI + LLM + evaluation
  system, deployed on AWS ECS, not just slides.

---

## 6. Related Documents

- [`USER_SCENARIOS.md`](./USER_SCENARIOS.md) — healthcare user scenarios and product implications.
- [`CONSULTATION_WORKFLOW.md`](./CONSULTATION_WORKFLOW.md) — the staged consultation workflow design.
- [`MEDICAL_AI_SAFETY_POLICY.md`](./MEDICAL_AI_SAFETY_POLICY.md) — the layered medical safety framework.
- [`PRD_EVALUATION_LAB.md`](./PRD_EVALUATION_LAB.md) — evaluation workbench requirements.
- [`EVALUATION_METHODOLOGY.md`](./EVALUATION_METHODOLOGY.md) — how safe behaviour is measured.
