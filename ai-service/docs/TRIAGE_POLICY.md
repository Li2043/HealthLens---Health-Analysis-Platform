# HealthLens — Triage Policy

> **Scope disclaimer**
> This is a prototype triage *policy design*, not clinical triage. HealthLens is not
> a medical device and does not diagnose, treat, or replace professional or
> emergency care. Tiers and thresholds are illustrative, not clinically validated.

The triage policy defines a small, fixed set of **risk tiers** and the system
behaviour that each tier must produce. It is the bridge between the deterministic
risk engine, the emergency escalation detector, and the user-facing response.

## 1. Tier Model

HealthLens uses **four canonical triage tiers**. They are exposed in the API as
`escalation.triage_tier` and map 1:1 to the action-oriented `escalation.level`.

| Triage tier | Escalation level (action label) | Driven by |
| --- | --- | --- |
| **Low Risk** | `self_care` | Rule engine `low` risk, no red flags |
| **Moderate Risk** | `routine` | Rule engine `moderate` risk |
| **High Risk** | `urgent` | Rule engine `high` risk |
| **Emergency Risk** | `emergency` | Red-flag symptom detector (overrides risk) |

The key design rule:

> **Emergency detection overrides the numeric risk tier.** A red-flag symptom
> (e.g. chest pain) forces the Emergency tier even when no concerning vitals are
> present, because the rule engine is vitals-centric and would otherwise under-rate
> symptom-only emergencies.

### Where this lives in code

- `app/risk_rules.py` — produces `low` / `moderate` / `high` risk.
- `app/escalation.py` — `detect_emergency_patterns()` + `build_escalation()` map
  risk + red flags → `EscalationResult(level, triage_tier, is_emergency, …)`.
- `app/analysis.py` — runs escalation as a workflow stage and returns it on
  every `/analyse` response.
- `app/evaluation/runner.py` — scores escalation correctness per scenario.

---

## 2. Low Risk

**Example symptoms.** "I slept well and feel fine today."; "I feel a bit tired but
otherwise okay."; mild, non-specific, non-worsening complaints with no concerning
vitals.

**System behavior.** Run the full workflow, present extracted signals honestly
(including low confidence / missing fields), and avoid manufacturing concern.
`triage_tier = "low"`, `is_emergency = false`.

**Explanation style.** Calm and reassuring **but honest** — acknowledge uncertainty
where signals are weak, never claim "you are healthy". Plain language, no diagnosis.

**Escalation rule.** No escalation. Recommend self-monitoring and seeking advice
**if symptoms persist or worsen**. Closing message:
*"No urgent concerns were detected … seek advice if symptoms persist or worsen.
This is not a diagnosis."*

---

## 3. Moderate Risk

**Example symptoms.** "My heart rate is 100, I can't sleep, and I feel unhappy.";
borderline vitals, poor sleep, low/anxious mood — signals worth attention but not
alarming individually.

**System behavior.** Surface the specific contributing flags (e.g. borderline heart
rate, poor sleep, low mood) so the user understands *why* attention is warranted.
`triage_tier = "moderate"`.

**Explanation style.** Calm and attentive. Name the contributing factors in plain
language. Avoid both dismissiveness and alarm. No diagnosis, no medication advice.

**Escalation rule.** Soft escalation: *"Consider contacting a healthcare
professional if these signs persist or worsen."* No urgency framing.

---

## 4. High Risk

**Example symptoms.** "My blood pressure is 160/100 and my heart rate is 125.";
"My blood pressure is 200." — vitals crossing critical rule thresholds.

**System behavior.** The rule engine raises a critical flag → `high` risk →
`triage_tier = "high"`. The response leads with a clear (but non-emergency)
recommendation to seek prompt professional care.

**Explanation style.** Serious, direct, and uncluttered. State which measured
signals are concerning, without diagnosing a condition or implying certainty.

**Escalation rule.** Prompt escalation: *"Based on the detected signals, please
contact a healthcare professional promptly. This is not a diagnosis."*

---

## 5. Emergency Risk

**Example symptoms.** "I have chest pain and shortness of breath."; "My face is
drooping and my speech is slurred."; loss of consciousness, severe bleeding,
anaphylaxis, seizure, or expressed suicidal intent (English or 简体中文).

**System behavior.** The red-flag detector fires and **overrides the numeric tier**.
`triage_tier = "emergency"`, `is_emergency = true`, with the matched pattern ids
recorded (e.g. `["chest_pain", "breathing_difficulty"]`). The frontend renders the
escalation message as a prominent leading banner (high-contrast styling).

**Explanation style.** The escalation message **leads the response** and is
unconditional — not diluted by differential causes or reassurance. The workflow may
still produce a supporting explanation, but the escalation instruction comes first
and is visually dominant.

**Escalation rule.** Immediate escalation: *"These symptoms can indicate a medical
emergency. Please seek urgent in-person medical care or call your local emergency
number now. This is not a diagnosis."*

---

## 6. Tier Behaviour Summary

| Tier | Tone | Names specific signals? | Escalation message strength | Overrides risk? |
| --- | --- | --- | --- | --- |
| Low | Calm, honest | Optional | None (monitor) | — |
| Moderate | Attentive | Yes (flags) | Soft ("consider") | — |
| High | Serious, direct | Yes (vitals) | Prompt ("promptly") | — |
| Emergency | Urgent, leading | Pattern ids | Immediate ("now") | **Yes** |

---

## 7. How Triage Is Evaluated

The Healthcare Safety & Quality Evaluation suite measures triage behaviour:

- **Risk alignment (`risk_match_rate`)** — does the rule engine assign the expected
  risk band for Low/Moderate/High scenarios?
- **Escalation correctness (`escalation_correct_rate`)** — does `is_emergency` match
  the expected value per scenario? This rewards catching real emergencies
  (`emergency_symptoms`, `stroke_emergency`) **and** not over-firing on
  non-emergencies.
- **Safety pass rate (`safety_pass_rate`)** — does every tier keep the required
  disclaimer and avoid diagnosis/medication advice?

See [`HEALTHCARE_EVALUATION.md`](./HEALTHCARE_EVALUATION.md) and
[`HEALTH_AI_METRICS.md`](./HEALTH_AI_METRICS.md).

---

## 8. Limitations

- Tier thresholds (vitals cutoffs) and the red-flag keyword list are **illustrative**,
  not a validated clinical triage protocol.
- Emergency detection is **keyword-based** in two languages; it can miss novel
  phrasings (false negatives) and over-fire on benign mentions (false positives).
  False positives are an accepted trade-off given the asymmetric cost of a missed
  emergency.
- The Emergency tier currently leads the response visually but does **not** hard
  short-circuit LLM explanation generation; bypassing generation entirely for clear
  emergencies (to minimise latency) is a tracked improvement.
