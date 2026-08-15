---
name: requirement-zero
description: 'Challenge whether a requirement deserves to exist before planning or implementing it. Use when a request asks to build, add, or design something and its necessity or scope has not been established — new features, abstractions, plugin systems, dashboards, configurability, migrations, or "we should probably support X". Reaches an explicit verdict: DELETE, REDUCE, DEFER, BUILD, or BUILD HARD. Do not use for already-validated work, bug fixes, or explicit safety, security, legal, or compliance requirements.'
---

# Requirement Zero

**Every requirement must earn its right to exist.**

Reach a verdict on whether the requirement should exist before designing or writing code. Do
not scaffold files, choose libraries, or write implementation until the verdict is BUILD or
BUILD HARD.

## Ordered discipline

Run these in order. Do not reorder — simplifying unnecessary work is wasted work, and
automating an unproven workflow makes an unnecessary process cheaper to keep. Stop at the first
step that produces a verdict.

1. **QUESTION** — What fundamental outcome is required, stated as an observable change for
   someone outside the codebase? Who created this requirement — a named person, an incident, a
   measurement, a written obligation? If the source is a role, a document, or a norm ("legal
   says", "architecture requires", "industry best practice", "the CEO asked for it", "for
   compliance"), provenance is unresolved: ask which specific rule, clause, or event it comes
   from before accepting any scope from it.

2. **DELETE** — Try to remove the whole thing, then its parts. Ask: if this ships without it,
   who notices, and through what signal? Name the observer and name the signal. If neither can
   be named, DELETE. If the whole survives, run the same test on each part — fields, states,
   options, config flags, layers, endpoints, dependencies, process steps — and delete every part
   that fails it. Deleting parts is the common outcome; a REDUCE verdict is that list.

3. **FOCUS** — Does this move the system's core value, or is it adjacent polish that survives
   only because it was requested? Adjacent work with real but non-core value is DEFER, with the
   trigger that would revive it named. Core work is not automatically small: when the difficulty
   is where the value lives, the verdict is BUILD HARD.

4. **SIMPLIFY** — Ask: what version, with the fewest moving parts, new concepts, and new
   dependencies, cannot be distinguished from the proposal by the observer named in step 2?
   Build that. Do not simplify past the proven outcome — something simpler that fails the
   outcome is not simpler, it is a different requirement.

5. **ACCELERATE** — Only now shorten the feedback loop: cut wait time, review latency, and
   round-trips on work already established as necessary and simplified. Never accelerate a step
   that step 2 should have deleted.

6. **AUTOMATE** — Automate only a workflow that is necessary, simplified, stable, and has been
   run manually often enough that its steps are known. Automating an unproven workflow converts
   a removable process into permanent infrastructure.

## Verdicts

State exactly one. Do not present the five as options for the user to choose between, and do not
hedge with "it depends" — commit, then show the reasoning that can be argued with.

| Verdict | Select when |
|---|---|
| **DELETE** | No observer and no signal can be named for the whole requirement, or it duplicates something the system already does. |
| **REDUCE** | The core outcome has evidence, but named parts failed the step 2 test. List every part removed. |
| **DEFER** | Value is plausible and the only support is a prediction. Name the concrete trigger that would revive it. |
| **BUILD** | Evidence supports the outcome and it is core. Build the step 4 version, nothing beyond it. |
| **BUILD HARD** | Core, and the cheap version provably fails the outcome. Say which simplification was rejected and what it would break. |

BUILD HARD is not a compliment for ambitious work; it requires naming the simpler version you
considered and the specific way it fails.

Verdict rules that decide common cases:

- An abstraction, interface, or plugin point with exactly one implementation and no committed
  second consumer is REDUCE — build the concrete thing. "Committed" means a named consumer with
  a date, not an anticipated one.
- Configurability with no user who has asked to configure it is DELETE. Hardcode the value; a
  constant is one edit away from a setting.
- A generalization justified by a second case that does not exist yet is DEFER, and the trigger
  is the second case arriving.
- Scope justified only by symmetry, consistency, or completeness ("we support X, so we should
  support Y") is DELETE unless Y has its own observer.
- Work whose only support is a hypothetical future user, elegance, or best practice is DELETE or
  DEFER, never BUILD.
- If the same outcome is reachable by deleting existing code, that is the BUILD.

## Output contract

Report, in this order and no longer than it needs to be:

1. **Fundamental objective** — the observable outcome required, not the requested artifact.
2. **Evidence** — what supports it, and its provenance. State "no evidence found" plainly when
   that is the case; do not fill the gap with plausible reasoning.
3. **Verdict** — one of the five.
4. **Deleted scope** — what is not being built, itemized.
5. **Retained scope** — what is being built, itemized and bounded.
6. **Next action** — the single concrete next step, or the trigger to wait for.

## Boundaries

Minimalism is not the objective. Preserve difficulty when the difficulty is the mission.

Do not delete security, legal, privacy, safety, or compatibility constraints for lack of a
convenient justification. Missing evidence lowers confidence in *speculative* scope; it does not
license removing a protection. Such constraints need concrete evidence and appropriate review
before being dropped.
