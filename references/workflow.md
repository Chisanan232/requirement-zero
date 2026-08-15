# Running the Workflow

Load this when applying the discipline to a live request and you need the procedure: what to do
first, when to stop, and how to handle requirements that arrive mid-implementation.

`SKILL.md` defines the six steps. This file is how to execute them in a session.

## Before step 1: decide whether to run at all

Run the full discipline when the request adds a capability, an abstraction, a dependency, a
process, or configurability, and its necessity has not been established.

Do not run it on: a bug fix restoring intended behavior; work already challenged and decided;
a mechanical change with a stated outcome (rename, version bump, formatting); an explicit safety,
security, or compliance directive from an owner. For these, note in one line that the requirement
is pre-validated and proceed. Challenging a settled decision again is its own kind of waste.

Ambiguous case: a large bug fix that implies new architecture. Fix the bug; run the discipline on
the architecture separately.

## Step order and stopping

Stop at the first step that produces a verdict:

- Step 1 cannot produce a verdict, only a resolved or unresolved objective. If provenance is
  unresolved and the scope is speculative, stop and ask — see `provenance.md`. Do not proceed to
  step 2 on a guessed objective; you will delete the wrong parts.
- Step 2 produces DELETE (nothing survives) or a deletion list. See `deletion.md`.
- Step 3 produces DEFER (adjacent, nobody blocked) or routes to BUILD / BUILD HARD. See
  `mission-alignment.md`.
- Step 4 sets the size of a BUILD. It cannot overturn a verdict; if step 4 reveals that even the
  smallest version is not worth it, return to step 2 and say so.
- Steps 5 and 6 apply to workflows and processes, not to feature requirements. Skip them for a
  single feature verdict and say nothing about them.

A verdict of REDUCE is the combination of "the core survived step 2" and "these parts did not."
It is the most common correct answer for a real request and should not be avoided in favor of a
cleaner-sounding DELETE or BUILD.

## Gathering evidence without stalling

Time-box the search. Check, in order: the ticket or request text itself; the code and tests for
existing usage; recent incidents or bug reports if accessible; then ask the human.

Do not ask the human for something you can determine yourself — if the question is "does anything
call this interface", read the code. Do ask when the question is about intent, priority, or an
obligation. One consolidated question beats three sequential ones.

If evidence is inaccessible, say "no evidence found" rather than constructing a plausible
justification. Manufactured justification is the failure this skill exists to prevent; producing
it yourself is worse than producing none.

## Reporting the verdict

Use the output contract in `SKILL.md`. Additional rules:

- Lead with the verdict, not the reasoning. The human should know the answer in the first line.
- Itemize deleted scope. "Simplified the design" is not reviewable; "removed the plugin registry,
  the YAML config, and the two unused adapters" is.
- Do not pad with alternatives you did not choose, beyond the one simpler version required for a
  BUILD HARD verdict.
- Do not apologize for a DELETE verdict or hedge it into a suggestion.
- Where a verdict rests on an assumption, mark the assumption in one clause so it can be
  contradicted cheaply.

## After a BUILD or BUILD HARD verdict

Implement only the retained scope. Specifically:

- Do not add the deleted parts back during implementation because they are "easy while I'm here."
  That is where deleted scope returns.
- If implementation reveals that the retained scope is insufficient, stop and re-state the
  verdict with the new information rather than silently expanding.
- If implementation reveals more removable scope, say so; a second REDUCE is a valid output.

## Requirements that arrive mid-implementation

A new requirement discovered while coding gets the same treatment, at a lower cost — because you
now know the code. Run steps 1 and 2 against it immediately rather than deferring the question to
review. "While I was in there" is the most common origin of unvalidated scope, and it never gets
challenged because it never appears as a request.

## Applying it to a plan

When reviewing a plan or task breakdown rather than a single request, run the parts test against
each task. Typical outcomes: tasks that exist only to support a deleted task, tasks producing
documents nobody reads, and setup tasks for infrastructure the retained scope does not need. Give
one verdict per task and one for the plan as a whole; do not average them into a single vague
assessment.
