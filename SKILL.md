---
name: requirement-zero
description: 'Challenge whether a requirement deserves to exist before planning or implementing it. Use when a request asks to build, add, or design something and its necessity or scope has not been established — new features, abstractions, plugin systems, dashboards, configurability, migrations, or "we should probably support X". Reaches an explicit verdict: DELETE, REDUCE, DEFER, BUILD, or BUILD HARD. Do not use for already-validated work, bug fixes, or explicit safety, security, legal, or compliance requirements.'
---

# Requirement Zero

**Every requirement must earn its right to exist.**

Reach a verdict on whether the requirement should exist before designing or writing code.

## Ordered discipline

Run these in order. Do not reorder — simplifying unnecessary work is wasted work, and
automating an unproven workflow makes an unnecessary process cheaper to keep.

1. **QUESTION** — What fundamental outcome is actually required? Who created this requirement,
   and what evidence supports it?
2. **DELETE** — Can the requirement, part, process, abstraction, or dependency be removed
   entirely?
3. **FOCUS** — If necessary, is it central to the mission, or adjacent polish?
4. **SIMPLIFY** — Find the smallest implementation delivering the proven outcome.
5. **ACCELERATE** — Shorten the feedback loop, only once the work is necessary and simplified.
6. **AUTOMATE** — Automate only a proven, necessary workflow.

## Verdicts

State exactly one:

- **DELETE** — the requirement does not earn its existence.
- **REDUCE** — real need, oversized proposed scope or solution.
- **DEFER** — plausible value, insufficient present evidence.
- **BUILD** — necessary and aligned with the fundamental objective.
- **BUILD HARD** — difficult and expensive, but attacks a mission-critical bottleneck and must
  not be simplified away.

Report the fundamental objective, the evidence, the scope deleted, the scope retained, and the
next action.

## Boundaries

Minimalism is not the objective. Preserve difficulty when the difficulty is the mission.

Do not delete security, legal, privacy, safety, or compatibility constraints for lack of a
convenient justification. Missing evidence lowers confidence in *speculative* scope; it does not
license removing a protection. Such constraints need concrete evidence and appropriate review
before being dropped.
