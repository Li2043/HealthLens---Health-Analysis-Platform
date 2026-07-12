# HealthLens — Medical AI Safety Policy

> **Scope disclaimer**
> HealthLens is a prototype and a portfolio/engineering demo. It is **not** a
> medical device, **not** medical advice, and **must not** be used for diagnosis,
> treatment, or clinical decision-making. This policy describes safety *design*,
> not regulatory clearance.

Safety is the defining design constraint of HealthLens. Because health queries are
risk-sensitive and asymmetric (a falsely reassuring answer is worse than an overly
cautious one), safety cannot be a single guardrail bolted onto a chatbot. It is
implemented as **five layers**, each with a distinct job. A request must pass
through all relevant layers; any layer can downgrade, reshape, or block a response.

| Layer | Name | Core question |
| --- | --- | --- |
| 1 | Medical Scope Detection | *Is this even something we should respond to, and with how much confidence?* |
| 2 | Unsafe Advice Prevention | *Does the response avoid diagnosis, dosing, and false certainty?* |
| 3 | Risk-aware Response Design | *Does behaviour change appropriately with risk level?* |
| 4 | Emergency Escalation Logic | *Is this an emergency that must lead with "seek urgent care"?* |
| 5 | Human Referral Strategy | *When should we hand off to a human/clinical pathway?* |

A guiding principle runs through all five layers:

> **Asymmetric caution.** When uncertain, HealthLens fails toward caution and
> escalation, never toward reassurance.

---

## Layer 1 — Medical Scope Detection

**What it does.** Determines whether input is in scope (a health-related query),
out of scope (non-health), or unsafe-in-scope (a health query asking for something
the system must not provide, e.g. a dose). It also establishes how much confidence
the system can legitimately have, via extraction confidence and
`missing_or_ambiguous_fields`.

**How it is implemented today.**
- The extractor produces structured signals with `extraction_confidence` and a
  `missing_or_ambiguous_fields` list (`StructuredHealthInput`).
- Validators ensure values (e.g. blood pressure) are only treated as present when
  evidenced in the source text.
- The `non_health_input` evaluation case asserts non-health text ("help me choose a
  laptop") produces no concerning health flags.

**Rationale.** A system that cannot tell *whether it should answer* — or *how
confident it may be* — cannot be safe. Scope detection is the gate that prevents
the model from confidently processing things it has no basis to process.

**Benefits.**
- Prevents confident output on low-signal or out-of-scope input.
- Makes uncertainty a first-class, propagated property rather than something the
  model papers over.

**Limitations.**
- Scope detection is currently **implicit** (driven by extraction + validators)
  rather than a dedicated classifier. Subtle out-of-scope or mixed inputs may not
  be cleanly separated. A dedicated scope/intent classifier is a tracked
  improvement.

---

## Layer 2 — Unsafe Advice Prevention

**What it does.** Prevents the response from crossing three bright lines:

1. **Medication dosing** — no drug names, doses, frequencies, or "take X".
2. **Definitive diagnosis** — no "you have <condition>" assertions.
3. **Unsupported certainty** — no confident claims the structured signals and rules
   do not support.

**How it is implemented today.**
- **Prevention (prompt-level):** the system prompt forbids diagnosis and medication
  advice, requires the non-diagnostic disclaimer, and constrains the model to the
  provided structured input and flags (`app/llm_service.py`).
- **Detection (output-level):** `app/safety_validator.py` checks that the
  disclaimer phrase is present and that diagnostic phrases ("you have hypertension")
  and medication phrases ("you should take medication") are absent, returning a
  `SafetyCheck.passed` flag.
- **Evaluation:** `unsafe_medication_request` asserts no dosage advice
  (`require_no_medication_advice`); `safety_pass_rate` tracks this across the suite.

**Rationale.** These three behaviours are where LLM health output causes the most
direct harm. Forbidding them at the prompt *and* detecting them on output gives
defence in depth — prevention reduces occurrence, detection catches leakage and
makes it measurable.

**Benefits.**
- Two-sided (prevent + detect) protection against the highest-harm outputs.
- Produces a regression-testable safety metric.
- The mandatory disclaimer ensures consistent non-diagnostic framing.

**Limitations.**
- The output detector is a **conservative string/intent matcher**, not a semantic
  guarantee. It can miss unsafe phrasing it does not enumerate (false negatives) and
  is English/keyword oriented. It should be treated as a safety *signal*, not proof
  of safety. Strengthening it (semantic classification, multilingual coverage) is a
  tracked improvement.

---

## Layer 3 — Risk-aware Response Design

**What it does.** Makes response *behaviour* a function of assessed risk level, so
the same engine responds differently to low, moderate, and high risk.

**Behaviour by risk level (target design):**

| Risk level | Tone & content | Recommended action |
| --- | --- | --- |
| **Low** | Calm, reassuring-but-honest; note uncertainty | Self-monitor; seek advice if persistent/worsening |
| **Moderate** | Calm, attentive; name the contributing flags | Consider contacting a healthcare professional |
| **High** | Serious, direct, uncluttered | Seek prompt professional / urgent care |

**How it is implemented today.**
- Risk level is computed deterministically (`app/risk_rules.py`) and passed to the
  explanation stage, which references the flags and risk level in plain language.
- The mock and OpenAI explanations both incorporate the risk level and flags,
  always closing with the professional-advice + non-diagnosis framing.

**Rationale.** A fixed response to all risk levels is unsafe in both directions: too
alarming for benign input, too soft for serious input. Tying behaviour to a
**deterministic** risk signal keeps this differentiation reproducible.

**Benefits.**
- Proportional responses reduce both unnecessary anxiety and dangerous
  under-reaction.
- Because risk is rule-based, the behaviour mapping is testable (`risk_match_rate`).

**Limitations.**
- Differentiation currently lives mostly in **content/wording** rather than a
  formal response-template-per-level. Making the risk→template mapping explicit
  (and evaluated for tone) is a tracked improvement.
- Risk thresholds are prototype values, not clinically validated cutoffs.

---

## Layer 4 — Emergency Escalation Logic

**What it does.** Detects emergency-pattern symptoms and ensures the response
**leads with an unconditional instruction to seek urgent / emergency in-person
care**, independent of (and overriding) the numeric risk level.

**How it is implemented today.**
- `app/escalation.py` provides a dedicated red-flag detector and escalation builder.
  Emergency-pattern symptoms produce an `EscalationResult` with `level="emergency"`
  and a leading, localised escalation message — **independent of and overriding the
  numeric risk level**. This runs as its own stage in both the live pipeline and the
  evaluation runner (with an `escalation` trace step).
- The system prompt additionally requires recommending professional help when
  symptoms are "concerning, unusual, persistent, or worsening."
- The `emergency_symptoms` and `stroke_emergency` evaluation cases assert
  `require_emergency_escalation`; `tests/test_escalation.py` covers detection,
  level mapping, English/中文 patterns, and the `/analyse` response shape.

**Rationale.** In an emergency, the most valuable action is fast, clear escalation —
not information. This must not depend on whether numeric vitals happened to be
present, and must not be diluted by caveats or differential causes.

**Benefits.**
- Protects the highest-stakes scenario (Scenario 2) with an explicit requirement.
- Decoupling escalation from numeric risk prevents symptom-only emergencies from
  slipping through a vitals-centric rule engine.

**Limitations (remaining, after implementing the escalation stage).**
- The numeric rule engine is still **vitals-centric**; symptom-only emergencies are
  now caught by the dedicated escalation detector rather than by the risk level.
  The escalation layer is therefore the safety net, and its **pattern list is
  keyword-based** — it can miss novel phrasings (false negatives) and fire on
  benign mentions (false positives). False positives are an accepted trade-off
  given the asymmetric cost of a missed emergency.
- The escalation message currently leads the result as a prominent banner but does
  **not** hard short-circuit LLM explanation generation; a future improvement is to
  fully bypass generation for clear emergencies to minimise latency.
- Pattern coverage is illustrative, not a validated clinical red-flag set.

---

## Layer 5 — Human Referral Strategy

**What it does.** Defines when HealthLens should stop trying to handle a situation
itself and route the user toward a human or clinical pathway.

**Referral triggers (design):**
- **High risk or emergency pattern** → urgent in-person / emergency care (Layer 4).
- **Persistent / worsening / unusual symptoms** → recommend a healthcare
  professional.
- **Sustained uncertainty** — low extraction confidence on a concerning query that
  the user keeps raising → recommend professional assessment rather than another
  low-confidence machine answer.
- **Out-of-scope or unsafe requests** (e.g. dosing) → decline + redirect to a
  professional, never improvise.

**How it is implemented today.**
- Every explanation closes with a recommendation to seek professional advice when
  symptoms are concerning, and frames itself as non-diagnostic
  (`app/llm_service.py`, `app/safety_validator.py`).

**Rationale.** An AI consultation prototype should know the boundary of its own
competence. A well-designed referral is not a failure — it is the correct product
behaviour for situations the system is not qualified to resolve.

**Benefits.**
- Keeps a clear human-in-the-loop boundary for high-risk and uncertain situations.
- Reinforces the product's scope (it is not a diagnosis or treatment engine).

**Limitations.**
- Referral is currently **advisory text**, not an integrated hand-off (no booking,
  no clinician routing, no continuity of record). In a real product this layer
  would connect to actual care pathways; here it is a designed boundary, documented
  honestly as such.

---

## Cross-Layer Summary

| Concern | Primary layer | Backup layer |
| --- | --- | --- |
| Out-of-scope / low-signal input | Layer 1 | Layer 3 |
| Diagnosis / dosing / overconfidence | Layer 2 | Layer 5 |
| Proportional response | Layer 3 | Layer 4 |
| Emergencies | Layer 4 | Layer 5 |
| Knowing when to hand off | Layer 5 | Layer 4 |

### How safety is verified

Safety behaviour is not assumed — it is measured by the evaluation lab:

- `safety_pass_rate` — share of cases passing the output safety check (Layer 2).
- `risk_match_rate` — share of cases with the expected risk level (Layer 3).
- Case-specific assertions — `require_no_medication_advice` (Layer 2),
  `require_professional_help_wording` (Layer 4), `expect_validation_error` (input
  guardrail / Layer 1).

See [`EVALUATION_METHODOLOGY.md`](./EVALUATION_METHODOLOGY.md).

### Known limitations (consolidated)

1. Detection is conservative and keyword-oriented; it is a safety signal, not a
   guarantee.
2. The rule engine is vitals-centric; symptom-only emergencies are now handled by a
   dedicated, keyword-based escalation stage (`app/escalation.py`) that can still
   miss novel phrasings or over-fire on benign mentions.
3. Risk thresholds are illustrative, not clinically validated.
4. Scope detection and human referral are implicit/advisory rather than fully
   integrated capabilities.

These are documented deliberately. For a healthcare AI product, **stating
limitations honestly is part of the safety strategy** — it prevents the demo from
being mistaken for a cleared clinical tool.
