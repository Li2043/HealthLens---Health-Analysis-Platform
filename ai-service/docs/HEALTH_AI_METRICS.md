# HealthLens — Product & Safety Metrics

> **Scope disclaimer**
> These are product/engineering success metrics for a prototype, not clinical
> outcome measures. HealthLens is not a medical device.

This document defines how HealthLens measures success. Metrics are grouped into five
categories. For each metric we state **what it is**, **how it is measured here**,
and — most importantly — **why it matters** for a safe healthcare consultation
product. Metrics already computed by the evaluation suite are marked **(live)**;
others are **(proposed)** with a clear measurement path.

A guiding principle: in healthcare AI, **safety metrics dominate quality metrics,
and quality metrics dominate engagement metrics.** A product that is engaging but
unsafe is a failure.

---

## 1. Extraction Metrics

### 1.1 Symptom / signal extraction accuracy
- **What.** Of the signals present in the input (heart rate, blood pressure, mood,
  sleep, symptoms), what fraction does the extractor identify correctly, without
  fabricating values?
- **How (live, proxy).** The evaluation suite computes a per-scenario
  `signal_match_score` against expected signals; `average_signal_match_score`
  aggregates it. Validators additionally enforce "no invented numbers" (e.g.
  `qualitative_bp`).
- **Why it matters.** Extraction is the foundation of the whole workflow. If the
  system mishears the input, every downstream stage (risk, escalation, explanation)
  is wrong. Fabricated values are a direct patient-safety risk — inventing "140/90"
  from "feels high" creates false precision the user may act on.

### 1.2 Extraction confidence calibration *(proposed)*
- **What.** Does reported `extraction_confidence` correlate with actual accuracy?
- **How.** Bucket scenarios by reported confidence; compare to measured accuracy.
- **Why it matters.** Honest uncertainty is a safety feature. A system that is
  confidently wrong is more dangerous than one that flags low confidence.

---

## 2. Safety Metrics (highest priority)

### 2.1 Unsafe response rate
- **What.** Fraction of responses that contain a diagnosis, medication/dosing
  advice, or are missing the required non-diagnostic disclaimer.
- **How (live).** `safety_validator.py` produces `SafetyCheck.passed`; the suite
  reports `safety_pass_rate`. Unsafe response rate = `1 − safety_pass_rate`.
- **Why it matters.** These are the highest-harm failure modes. A single unsafe
  dosing instruction can cause real-world harm, so this metric has a near-zero
  tolerance target.

### 2.2 False reassurance rate
- **What.** Fraction of *concerning* scenarios where the response reassures or
  under-states risk instead of escalating (e.g. telling a chest-pain user it is
  "probably nothing").
- **How (live, proxy).** For emergency/high scenarios, the suite requires
  professional-help wording (`require_professional_help_wording`) and correct
  escalation (`require_emergency_escalation`); failures on these are false
  reassurance. A dedicated reassurance-language classifier is **proposed** to
  strengthen this.
- **Why it matters.** This is the *asymmetric* failure: a falsely reassuring answer
  to a serious symptom is far more harmful than an overly cautious one. It is the
  metric most aligned with patient harm.

### 2.3 Escalation precision (and recall)
- **What.** **Precision** — of responses flagged emergency, how many should be?
  **Recall** — of true emergencies, how many were flagged?
- **How (live, proxy).** `escalation_correct_rate` checks `is_emergency` against the
  expected value per scenario (rewards catching `emergency_symptoms` /
  `stroke_emergency` and *not* over-firing elsewhere). Precision/recall split is
  **proposed** as the case set grows.
- **Why it matters.** Recall protects against missed emergencies (the catastrophic
  error). Precision protects trust and usability — an "everything is an emergency"
  system is quickly ignored, which itself becomes unsafe.

---

## 3. Quality Metrics

### 3.1 Risk classification accuracy
- **What.** Does the assigned risk tier match the expected tier for each scenario?
- **How (live).** `risk_match_rate` over the suite (with `acceptable_risk_levels`
  for genuinely ambiguous cases).
- **Why it matters.** The risk tier drives response tone and escalation. Misranking
  risk propagates into inappropriate behaviour for the user.

### 3.2 Explanation consistency
- **What.** For the same input, does the explanation stay stable in meaning, tone,
  and safety framing (especially across runs and providers)?
- **How (live for mock; proposed for OpenAI).** Mock mode is deterministic, giving a
  consistency baseline. For OpenAI, **proposed**: run N times, measure variance in
  safety-check pass, risk references, and embedding similarity of explanations.
- **Why it matters.** Inconsistent health explanations erode trust and can produce
  an unsafe variant on some runs. Consistency is a precondition for relying on the
  model at all.

---

## 4. Product Metrics

### 4.1 Consultation completion rate *(proposed)*
- **What.** Fraction of started consultations that reach a final response (signals →
  risk → escalation → explanation) without error or abandonment.
- **How.** Instrument the `/analyse` flow: started vs. successfully returned.
- **Why it matters.** A safe answer the user never receives delivers no value.
  Completion is the basic measure of the product actually working end to end.

### 4.2 Clarity score *(proposed)*
- **What.** How understandable is the explanation to a non-expert?
- **How.** Readability scoring (e.g. grade level) plus lightweight human or
  LLM-as-judge ratings on a 1–5 clarity scale.
- **Why it matters.** Anxious users under stress cannot act on jargon. Clarity is
  what turns a correct answer into a useful one — and a clear "seek urgent care"
  is the difference between escalation that works and one that is ignored.

### 4.3 Trust proxy metrics *(proposed)*
- **What.** Indirect signals of user trust: re-use rate, time-on-result, whether
  users follow the recommended next step, explicit thumbs-up/down.
- **How.** Frontend interaction analytics + optional feedback control.
- **Why it matters.** Trust is the currency of a consultation product. Over- or
  under-escalation both erode it; these proxies catch trust problems before they
  show up as churn. (Must be privacy-preserving — see Non-goals in the PRD.)

---

## 5. Reliability Metrics

### 5.1 Latency
- **What.** Time to return a full analysis (and, separately, time-to-escalation for
  emergencies).
- **How (live).** The suite reports `average_latency_ms` per run; the API enforces
  `ANALYSE_TIMEOUT_SECONDS`.
- **Why it matters.** In an emergency, speed is a safety property — the escalation
  message must appear quickly. Generally, latency drives whether the product feels
  usable. Tracking time-to-escalation separately is **proposed**.

### 5.2 Provider stability
- **What.** Success rate and fallback behaviour of the LLM/extractor providers
  (mock vs OpenAI), including graceful degradation when keys are missing.
- **How (live, partial).** `get_llm_service()` falls back to mock on missing key;
  `is_openai_provider_misconfigured()` surfaces misconfiguration. **Proposed**:
  track live error/timeout/fallback rates over time.
- **Why it matters.** A consultation product must fail safe, not silently degrade
  into unsafe or empty answers. Provider stability ensures the safety-managed
  workflow is the one actually serving users.

---

## 6. Metric Priority & Targets (illustrative)

| Priority | Metric | Direction | Illustrative target |
| --- | --- | --- | --- |
| P0 | Unsafe response rate | minimise | ~0% |
| P0 | False reassurance rate | minimise | ~0% on concerning cases |
| P0 | Escalation recall | maximise | 100% on emergency cases |
| P1 | Escalation precision | maximise | high; tolerate some over-escalation |
| P1 | Risk classification accuracy | maximise | high |
| P1 | Extraction accuracy (no fabrication) | maximise | high |
| P2 | Explanation consistency / clarity | maximise | stable, plain |
| P2 | Latency / provider stability | optimise | within timeout, fail safe |
| P3 | Completion / trust proxies | observe | trend up |

> Targets are illustrative for a prototype. The ordering is the point: **P0 safety
> metrics gate everything else.**

See [`HEALTHCARE_EVALUATION.md`](./HEALTHCARE_EVALUATION.md) for how these are
measured and [`TRIAGE_POLICY.md`](./TRIAGE_POLICY.md) for tier behaviour.
