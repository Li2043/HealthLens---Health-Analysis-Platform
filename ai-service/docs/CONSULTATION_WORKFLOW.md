# HealthLens — Healthcare Consultation Workflow Design

> **Scope disclaimer**
> This document describes the *designed* consultation workflow for a prototype.
> HealthLens is not a medical device and does not provide diagnosis or treatment.

The central design idea of HealthLens is that a safe healthcare consultation is a
**workflow**, not a single model call. Each stage has a narrow job, an inspectable
output, and a clear safety responsibility. This makes the system auditable: a
reviewer can see *why* the product responded the way it did.

---

## 1. Workflow Overview

```
            User Input
                │
                ▼
   ┌───────────────────────────┐
   │  Symptom Signal Extraction │   free text → structured signals
   └───────────────────────────┘
                │
                ▼
   ┌───────────────────────────┐
   │      Risk Assessment       │   deterministic risk rules
   └───────────────────────────┘
                │
                ▼
   ┌───────────────────────────┐
   │     Safety Validation      │   gate inputs / verify outputs
   └───────────────────────────┘
                │
                ▼
   ┌───────────────────────────┐
   │   Explanation Generation   │   constrained, grounded LLM
   └───────────────────────────┘
                │
                ▼
   ┌───────────────────────────┐
   │  Escalation Recommendation │   what should the user do next?
   └───────────────────────────┘
                │
                ▼
            Final Response
```

> **Implementation note.** In the current code (`app/analysis.py`) the order is
> extraction → risk → **explanation → safety validation**, where safety validation
> is an *output* check. The target design below treats Safety Validation as a stage
> that both **gates** what may be explained and **verifies** what was explained.
> Where the prototype differs, it is called out under "Current implementation".

Before all stages, an **Input Guardrail** runs (length and basic input validation,
`MAX_INPUT_CHARS`, controlled `INPUT_TOO_LARGE` error). It is shown as part of the
"User Input" step.

---

## 2. Stage 1 — Symptom Signal Extraction

**Purpose:** Convert unstructured, emotional free text into structured, inspectable
signals: heart rate, blood pressure, mood, sleep quality, symptoms — each with a
status (`absent` / `partial` / `complete` / `ambiguous`) and supporting evidence.

**Logic:**
- A provider (`mock` or `openai`) implements an `extract()` method returning a
  `StructuredHealthInput`.
- The result carries `extraction_confidence`, `missing_or_ambiguous_fields`, and
  `extraction_evidence` so downstream stages and the UI can reason about *quality*,
  not just values.
- Validators (`extraction_validator.py`) enforce that, e.g., blood pressure is only
  treated as present when it actually appears in the source text.

**Design rationale:**
- Structuring first makes everything after it auditable. A reviewer can see exactly
  what the system "heard" before any risk or language is generated.
- Explicit confidence + missing-fields is what lets the product *preserve
  uncertainty* (User Scenarios 1 and 4) instead of guessing.

**Healthcare considerations:**
- **Never fabricate clinical values.** Qualitative phrasing ("blood pressure feels
  high") must not become a number. This is a patient-safety property, enforced by
  validation and checked by the `qualitative_bp` evaluation case.
- Low confidence must propagate; a vague input should not yield a confident result.

**Current implementation:** Built — `app/extractor.py`,
`app/extraction_validator.py`, `StructuredHealthInput` in `app/schemas.py`.

---

## 3. Stage 2 — Risk Assessment

**Purpose:** Assign an overall risk level (`low` / `moderate` / `high`) and a list
of explicit **flags** from the structured signals.

**Logic (deterministic, in `app/risk_rules.py`):**
- Vitals thresholds, e.g. systolic ≥ 180 or diastolic ≥ 120 → critical flag;
  systolic ≥ 140 or diastolic ≥ 90 → elevated; heart rate > 120 → very elevated,
  > 100 → elevated, 95–100 → borderline.
- Mood (`anxious` / `stressed` / `low`), poor sleep, and incomplete measurements
  each contribute flags.
- Risk level is computed from flags: any critical flag → `high`; non-borderline
  flags → `moderate`; otherwise `low`.

**Design rationale:**
- Risk is computed by **deterministic rules, not the LLM.** This is deliberate: the
  most safety-relevant decision in the pipeline should be reproducible, testable,
  and explainable, not subject to model variance.
- Flags are human-readable and become the grounding facts for the explanation
  stage, which prevents the model from inventing its own reasoning.

**Healthcare considerations:**
- Thresholds are illustrative prototype values, **not** validated clinical cutoffs.
  Real use would require clinically governed thresholds and review.
- The current engine is **vitals-centric**: symptom-only emergencies (chest pain)
  may not raise the numeric level. This is the key limitation that motivates the
  Escalation stage (Section 6) and Layer 4 of the safety policy.

**Current implementation:** Built — `app/risk_rules.py`, `RiskResult` schema.

---

## 4. Stage 3 — Safety Validation

**Purpose:** Enforce medical-safety constraints. In the target design this stage
has two roles: **(a) gate** — decide what may be explained or whether to short-
circuit to escalation; **(b) verify** — check generated text for unsafe content.

**Logic:**
- Verification (built, `app/safety_validator.py`): the explanation must contain the
  required disclaimer ("not a medical diagnosis") and must **not** contain
  diagnostic assertions ("you have hypertension") or medication advice
  ("you should take medication"). Output is a `SafetyCheck` with a `passed` flag.
- Gating (designed): before explanation, detect out-of-scope or unsafe requests
  (e.g. "what dose should I take?") and route them to a safe templated response
  instead of free generation.

**Design rationale:**
- Two-sided safety is more robust than either alone. Gating prevents the model from
  being asked to do something unsafe; verification catches anything that slips
  through.
- A deterministic checker on model output gives a measurable, regression-testable
  safety signal (used as `safety_pass_rate` in evaluation).

**Healthcare considerations:**
- The verifier is intentionally **conservative** — it is a string/intent check, not
  a guarantee. It can produce false negatives (unsafe phrasing it does not match)
  and false positives. Limitations are documented in the safety policy.
- The disclaimer requirement ensures every response is framed as non-diagnostic.

**Current implementation:** Verification built; input **gating** is partially built
(unsafe medication requests are covered by the system prompt and the
`unsafe_medication_request` evaluation case) and is a tracked improvement to make a
first-class pre-generation gate.

---

## 5. Stage 4 — Explanation Generation

**Purpose:** Produce a calm, plain-language explanation of the structured signals
and the rule-based risk result.

**Logic (`app/llm_service.py`):**
- A constrained system prompt instructs the model to: not diagnose, not prescribe,
  always state it is not a medical diagnosis, recommend professional advice when
  symptoms are concerning, use plain text, and **base the explanation only on the
  provided structured input and flags**.
- `mock` mode produces a deterministic explanation for tests/evaluation; `openai`
  mode calls the live API with the same constraints. Output is stripped of Markdown.

**Design rationale:**
- The LLM's job is **narrow**: explain, not decide. Risk was already decided
  deterministically; the model translates it into empathetic, readable language.
- Grounding the prompt in the structured input and flags reduces hallucination —
  the model is told what facts it may use.

**Healthcare considerations:**
- Tone is a requirement (Scenario 3): calm, non-dismissive, non-alarming.
- The model must not reintroduce certainty the rules did not establish (e.g.
  turning "moderate risk" into "you're fine").

**Current implementation:** Built — `MockLLMService` and `OpenAILLMService`.

---

## 6. Stage 5 — Escalation Recommendation

**Purpose:** Decide and clearly state **what the user should do next**, with special
handling for emergency patterns.

**Logic (implemented in `app/escalation.py`):**
- A red-flag detector (`detect_emergency_patterns`) scans the raw user text for
  emergency symptom patterns (chest pain, breathing difficulty, stroke signs, loss
  of consciousness, severe bleeding, anaphylaxis, seizure, suicidal ideation) in
  both English and 简体中文.
- `build_escalation` maps the situation to an escalation level:
  - emergency pattern detected → `emergency` (overrides numeric risk);
  - `high` risk → `urgent`;
  - `moderate` risk → `routine`;
  - `low` risk → `self_care`.
- Each level carries a localised `recommended_action`. The frontend renders this as
  a banner that **leads the result**, styled most prominently for emergencies.

**Design rationale:**
- Escalation is the single most valuable decision the product makes in a serious
  case (Scenario 2). Making it an explicit stage — rather than a sentence the model
  may or may not include — is what makes it reliable.
- Separating escalation from explanation means the urgent message is not diluted by
  informational caveats.

**Healthcare considerations:**
- For emergencies, **speed and clarity beat completeness.** The escalation message
  must not wait on a slow generation call and must not be hedged.
- Escalation copy should avoid implying the system has confirmed an emergency; it
  recommends seeking care, it does not diagnose one.

**Current implementation:** Built — `app/escalation.py` is a first-class stage in
both the live pipeline (`app/analysis.py`) and the evaluation runner (with its own
`escalation` workflow-trace step). `EscalationResult` is returned on every
`/analyse` response. Emergency detection is symptom-driven and overrides the
vitals-centric risk level, closing the gap previously noted here. Coverage:
`emergency_symptoms` and `stroke_emergency` evaluation cases assert
`require_emergency_escalation`, plus unit tests in `tests/test_escalation.py`.

---

## 7. Stage 6 — Final Response

**Purpose:** Assemble the user-facing response and the auditable record.

**Logic (`AnalysisResponse` in `app/schemas.py`):**
- Returns the structured input, risk result, explanation, safety check, and the
  active extractor/LLM providers (plus any `provider_warning`), localised to the
  requested language (`en` / `zh`).
- The evaluation runner additionally emits a **`workflow_trace`** — per-stage
  status and duration — so each run is inspectable end to end.

**Design rationale:**
- Returning the *whole chain* (signals → risk → safety → explanation) rather than
  just prose is what makes HealthLens a *workflow* product. It supports debugging,
  evaluation, and trust.

**Healthcare considerations:**
- Every response carries the non-diagnostic framing and, where relevant, the
  provider/mode so reviewers know whether output came from mock or live LLM.

**Current implementation:** Built — `app/analysis.py`, `app/main.py`,
`app/evaluation/runner.py` (trace).

---

## 8. Stage → Code → Safety Traceability

| Stage | Code | Safety layer (policy) | Evaluation signal |
| --- | --- | --- | --- |
| Input guardrail | `app/config.py`, `app/errors.py` | Layer 1 | `long_input_guardrail` |
| Signal extraction | `app/extractor.py`, `extraction_validator.py` | Layer 1, 3 | signal match score |
| Risk assessment | `app/risk_rules.py` | Layer 3 | `risk_match_rate` |
| Safety validation | `app/safety_validator.py` | Layer 2 | `safety_pass_rate` |
| Explanation generation | `app/llm_service.py` | Layer 2, 3 | `pass_rate` |
| Escalation recommendation | (in explanation today) | Layer 4, 5 | `emergency_symptoms` |
| Final response / trace | `app/analysis.py`, `evaluation/runner.py` | — | `workflow_trace` |

See [`MEDICAL_AI_SAFETY_POLICY.md`](./MEDICAL_AI_SAFETY_POLICY.md) for the layers
and [`EVALUATION_METHODOLOGY.md`](./EVALUATION_METHODOLOGY.md) for the metrics.
