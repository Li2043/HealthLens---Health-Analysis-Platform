# HealthLens — User Personas

> **Scope disclaimer**
> Personas describe target users of a prototype consultation workflow. HealthLens is
> not a medical device and does not provide diagnosis or treatment.

These personas turn the abstract "anxious health user" into concrete people, so
product, workflow, and safety decisions can be checked against real motivations and
behaviours. They map directly to the scenarios in
[`USER_SCENARIOS.md`](./USER_SCENARIOS.md) and the triage tiers in
[`TRIAGE_POLICY.md`](./TRIAGE_POLICY.md).

Each persona includes: **background**, **motivation**, **frustration**,
**behavior**, and **AI healthcare implications**.

---

## Persona 1 — Mia, the Anxiety-Driven Health Searcher

> *"I just need to know if I should be worried."*

**Background.** Mia, 27, marketing professional in a large city. Health-literate
enough to search, not enough to interpret. Slightly health-anxious; one bad search
result can ruin her evening. Uses her phone late at night.

**Motivation.** Emotional reassurance first, information second. She wants the
worry to resolve — ideally to hear "this is probably okay," but in a way she can
trust.

**Frustration.** Search engines escalate her anxiety: every symptom links to a
worst-case disease. Generic chatbots swing between scary lists and glib "don't
worry." Neither helps her calibrate, and the cycle of searching makes her *more*
anxious.

**Behavior.** Types feelings, not measurements ("my blood pressure feels high",
"my heart is racing"). Searches repeatedly, late at night, across multiple sources.
Reacts strongly to tone.

**AI healthcare implications.**
- Tone is a feature: responses must be **calm but never falsely reassuring**.
- Must **not fabricate data** from qualitative phrasing ("feels high" ≠ a number).
- Should gently convert anxiety into a constructive next step (measure, monitor,
  seek advice if persistent) rather than feeding the search spiral.
- Maps to **Scenario 3 (anxiety-driven)**, triage **Low/Moderate**.

---

## Persona 2 — David, the Symptom Clarification User

> *"Something feels off, but I can't put my finger on it."*

**Background.** David, 41, operations manager, busy and pragmatic. Not anxious by
nature; he just wants a quick read before deciding whether it's worth a clinic
visit. Time-poor.

**Motivation.** Clarity and triage. He wants to understand *severity* and *what to
do next* — self-monitor, book a GP, or act now — without reading an article.

**Frustration.** His symptoms are vague ("a bit dizzy and tired lately"), so search
gives him everything and nothing. He doesn't know which details matter, and he
won't spend 20 minutes figuring it out.

**Behavior.** Short, factual inputs. Wants a fast, structured answer. Will provide
more detail *if* the system tells him exactly what would help. Low tolerance for
fluff.

**AI healthcare implications.**
- Must **preserve and surface uncertainty** (extraction confidence, missing fields)
  instead of guessing.
- Should **ask for / point to the specific detail** that would change the
  assessment (duration, recurrence, vitals).
- Structured, scannable output (signals → risk → next step) beats prose.
- Maps to **Scenarios 1 & 4 (symptom uncertainty / ambiguity)**, triage
  **Low/Moderate**.

---

## Persona 3 — Sofia, the Risk-Sensitive User

> *"I have chest pain — what do I do right now?"*

**Background.** Sofia, 58, caring for an elderly parent and conscious of her own
cardiovascular risk. She or a family member sometimes has genuinely concerning
symptoms. Higher stakes, lower tolerance for ambiguity.

**Motivation.** Decisive guidance in a potentially serious moment. The single most
valuable output is a clear "seek urgent care now" when warranted.

**Frustration.** A chatbot that lists possible causes, asks follow-up questions, or
offers a benign explanation wastes time and can read as reassurance — exactly when
speed matters most. She fears being told "it's probably fine" and being wrong.

**Behavior.** Describes acute symptoms directly (chest pain, shortness of breath,
slurred speech). Under stress, scans for the one instruction that tells her what to
do. May be acting on behalf of someone else.

**AI healthcare implications.**
- **Emergency escalation must lead the response**, be unconditional, and not be
  diluted by differential causes or reassurance.
- Escalation must be **symptom-driven**, independent of whether numeric vitals are
  present (handled by `app/escalation.py`, overriding the vitals-centric risk tier).
- Bias toward **over-escalation** (false positives acceptable; a missed emergency is
  not).
- Maps to **Scenario 2 (risk-sensitive)**, triage **Emergency**.

---

## Persona → Scenario → Triage → Safety Map

| Persona | Primary scenario | Triage tier(s) | Dominant safety concern |
| --- | --- | --- | --- |
| 1 — Mia (anxiety-driven) | Scenario 3 | Low / Moderate | No false reassurance; no fabricated data; calm tone |
| 2 — David (clarification) | Scenarios 1 & 4 | Low / Moderate | Preserve uncertainty; no fabricated specificity |
| 3 — Sofia (risk-sensitive) | Scenario 2 | Emergency | Decisive escalation; never miss an emergency |

---

## Design Implications Common to All Personas

1. **Calm, plain, non-alarming language** — every persona is stressed or rushed.
2. **Honesty about uncertainty** — none are served by confident guessing.
3. **A clear next step** — all three ultimately want to know *what to do*.
4. **Asymmetric caution** — when in doubt, escalate rather than reassure.

See [`AI_HEALTH_PRD.md`](./AI_HEALTH_PRD.md) for how these personas shape MVP scope
and success metrics.
