# Product Requirements Document — HealthLens

**Product:** HealthLens — Safe AI Healthcare Consultation Workflow
**Status:** Prototype / portfolio demo
**Owner:** Product (AI Healthcare)
**Last updated:** 2026-05

> **Scope disclaimer**
> HealthLens is a prototype and design exploration. It is **not** a medical device,
> not medical advice, and must not be used for diagnosis, treatment, or clinical
> decisions. This PRD describes a demo product, written in real PRD format.

---

## 1. Background

Consumer health questions are one of the most common — and most sensitive — uses of
general-purpose chat assistants. People ask "is this serious?" far more often than
they ask a clinician, because chat is instant, free, and private. But general LLM
chat is structurally mismatched to health queries: it optimises for a fluent answer,
while health queries demand calibrated uncertainty, safety constraints, and
decisive escalation.

The result is a product gap. Today users get either (a) generic search that buries
the important signal in noise, or (b) a confident chatbot that may diagnose,
reassure, or advise unsafely. Neither reliably does the one thing that matters most:
help the user understand severity and take the safe next step.

HealthLens explores the missing middle: a **structured consultation workflow** that
treats the LLM as one constrained component inside a safety-managed pipeline
(extraction → risk → escalation → explanation → validation), with safety and
escalation as first-class, evaluated behaviours.

---

## 2. Target Users

**Primary: the anxious self-checker.** A non-expert adult experiencing symptoms or
worry who wants a quick, calm read on "should I be concerned, and what do I do?"
They are emotionally activated and not medically literate.

**Secondary: the caregiver.** Someone checking on a family member's symptoms
(parent, child, elderly relative), often under time pressure.

**Tertiary (internal): the reviewer / stakeholder.** A product, clinical-safety, or
engineering reviewer who needs to inspect *why* the system responded as it did
(workflow trace, safety checks, evaluation metrics).

Out of audience: clinicians seeking a diagnostic tool, and users seeking treatment
or medication guidance (explicitly redirected, see Non-goals).

---

## 3. Pain Points

| # | Pain point | Consequence today |
| --- | --- | --- |
| P1 | Can't gauge severity of vague symptoms | Either ignore something serious or over-worry |
| P2 | Generic chat may reassure unsafely | Delayed care for real emergencies (highest harm) |
| P3 | Generic chat may diagnose / prescribe | Users act on unsafe, unqualified advice |
| P4 | Output is jargon-heavy or alarmist | Anxious users can't act on it |
| P5 | No transparency into reasoning | Users and reviewers can't trust or audit the answer |
| P6 | Emergencies not handled decisively | The one high-stakes case is treated like any other |

---

## 4. Core Use Cases

Anchored to [`USER_SCENARIOS.md`](./USER_SCENARIOS.md):

1. **Symptom uncertainty** — "I feel dizzy and tired recently." → understand
   severity; system preserves uncertainty and invites useful detail. *(Low/Moderate)*
2. **Risk-sensitive emergency** — "Chest pain and shortness of breath." → system
   leads with urgent escalation, no diagnosis. *(Emergency)*
3. **Anxiety-driven inquiry** — "My blood pressure feels high." → calm tone, no
   invented numbers, gentle nudge to measure/seek advice. *(Low/Moderate)*
4. **Ambiguous symptoms** — "I feel a bit off but not sure why." → honest low-signal
   handling, no fabricated specificity. *(Low)*
5. **Unsafe request** — "What dose should I take?" → refuse dosing, redirect to a
   professional. *(Safety guardrail)*
6. **Reviewer audit** — inspect workflow trace + safety/quality metrics for any run.

---

## 5. MVP Scope

**In scope (built today):**
- Free-text input (typed or voice) in English / 简体中文, in-memory only (no storage).
- Workflow: input guardrail → signal extraction → deterministic risk assessment →
  **emergency escalation** → constrained LLM explanation → output safety validation.
- **Four-tier triage** (Low / Moderate / High / Emergency) with tier-appropriate
  behaviour and a leading escalation banner for emergencies.
- Mock provider by default; OpenAI provider when configured (graceful fallback).
- **Healthcare Safety & Quality Evaluation** suite + UI tab (safety, risk alignment,
  escalation correctness, signal match, latency) with per-scenario workflow trace.
- Backend reliability: `/health`, `/version`, timeouts, controlled JSON errors,
  input length guardrail; Dockerised, deployable to AWS ECS.

**Explicitly out of MVP:** accounts, history/persistence, multi-turn dialogue,
images/labs, integrations with real care pathways, non-CN/EN languages.

---

## 6. Success Metrics

Full definitions in [`HEALTH_AI_METRICS.md`](./HEALTH_AI_METRICS.md). MVP headline
metrics, in priority order:

- **P0 — Safety:** unsafe response rate ≈ 0; false reassurance rate ≈ 0 on
  concerning scenarios; **emergency escalation recall = 100%** on emergency cases.
- **P1 — Quality:** risk classification accuracy and extraction accuracy (no
  fabricated values) high; escalation precision high (tolerate some over-escalation).
- **P2 — Experience:** explanation clarity/consistency; latency within timeout;
  provider stability (fail safe to mock).
- **P3 — Engagement (observe only):** consultation completion rate, trust proxies.

Live suite signals today: `safety_pass_rate`, `escalation_correct_rate`,
`risk_match_rate`, `average_signal_match_score`, `average_latency_ms`.

---

## 7. Future Roadmap

**Now (built):** structured workflow, four-tier triage, emergency escalation stage,
safety & quality evaluation suite, bilingual UI, ECS deployment.

**Next:**
- Hard short-circuit to escalation for clear emergencies (minimise time-to-escalation).
- Expand red-flag coverage; add precision/recall split for escalation.
- LLM-/human-judged explanation clarity & consistency scoring in the suite.
- Pre-generation safety **gate** (not just post-generation validation).

**Later:**
- Multi-turn clarifying questions (ask for the detail that changes the answer).
- Real referral hand-off (signpost to verified local services / emergency numbers).
- Broader language support; accessibility audit.
- Clinically governed thresholds and red-flag sets via expert review.

---

## 8. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| **Missed emergency** (false negative) | Severe (patient harm) | Dedicated red-flag detector overriding risk; recall = top metric; bias toward over-escalation |
| **Unsafe advice** (diagnosis/dosing) | Severe | Constrained prompt + output safety validation + scenario tests; refusal of dosing requests |
| **False reassurance** | Severe | Asymmetric scoring; professional-help wording required on concerning cases |
| **Over-escalation** ("everything is urgent") | Erodes trust → ignored warnings | Escalation precision metric; tiered (not binary) responses |
| **Model variance** (live OpenAI) | Inconsistent/unsafe variants | Mock default for regression; consistency evaluation; safety validation on every output |
| **Misuse as a real medical tool** | Reputational / user harm | Persistent disclaimers; explicit Non-goals; not a device |
| **Privacy** (sensitive input) | Trust / compliance | In-memory only, no storage; no PII collection in MVP |

---

## 9. Non-goals

HealthLens deliberately does **not**:

- diagnose conditions or assert a clinical diagnosis;
- recommend medications, doses, or treatments;
- replace clinicians, triage nurses, or emergency services;
- store user health data or build user profiles (MVP is stateless, in-memory);
- provide continuous monitoring, integrate with EHRs/devices, or claim regulatory clearance;
- guarantee clinical correctness — "pass" means conformance to the safety/quality
  design, not medical accuracy.

Stating these is itself a product decision: it keeps scope, safety, and user
expectations aligned, and prevents the demo from being mistaken for a cleared
clinical product.

---

## 10. Related Documents

- [`PROJECT_POSITIONING.md`](./PROJECT_POSITIONING.md) · [`USER_SCENARIOS.md`](./USER_SCENARIOS.md)
- [`CONSULTATION_WORKFLOW.md`](./CONSULTATION_WORKFLOW.md) · [`TRIAGE_POLICY.md`](./TRIAGE_POLICY.md)
- [`MEDICAL_AI_SAFETY_POLICY.md`](./MEDICAL_AI_SAFETY_POLICY.md)
- [`HEALTH_AI_METRICS.md`](./HEALTH_AI_METRICS.md) · [`HEALTHCARE_EVALUATION.md`](./HEALTHCARE_EVALUATION.md)
