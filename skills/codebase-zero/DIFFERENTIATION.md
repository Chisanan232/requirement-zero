# What Codebase Zero overlaps with, and where it differs

There is a lot of existing work on removing code. Some of it is better than this skill at what it
does. This document states the overlap honestly, so that a reader can decide whether they need this
at all — and so that if the answer is no, they can go use the better tool.

That is not a rhetorical gesture. A skill that cannot say when it is the wrong choice has not
applied its own discipline to itself.

## Where the overlap is real

**Static analyzers and dead-code detectors** — unused-symbol detection, unreachable-code analysis,
unused-dependency checks, linters. These are *better than this skill* at what they do, and the gap
is not close. They are exhaustive over the whole repository, they are deterministic, they run in CI,
and they do not hallucinate a caller that is not there. Their scope is "is this symbol referenced",
which they answer definitively for statically resolvable references.

If your question is "which symbols in this package are unreferenced", run the analyzer. Codebase
Zero will be slower and less complete.

**Code-minimization and YAGNI-oriented audit passes** — whole-repo sweeps that flag
over-engineering, speculative generality, and unnecessary abstraction. The overlap here is
substantial and honest: the SIMPLIFY verdict covers ground these tools already cover, and on a case
like a single-implementation abstraction behind a registry and a config file, the conclusion is the
same one.

**Refactoring and simplification skills** — code quality, duplication, reuse. The CONSOLIDATE
verdict overlaps directly with duplication detection.

So on three of the six verdicts — DELETE for genuinely dead code, SIMPLIFY, CONSOLIDATE — a good
existing tool reaches a similar answer, sometimes with better coverage.

## Where the difference is

The difference is not in finding removal candidates. It is in the three answers that are not
removal, and in what evidence is required before removal is recommended.

**1. The verdict set includes retention as a first-class outcome, not a null result.**

KEEP and INVEST are not "the tool found nothing here". They are conclusions with the same seven
required fields as a deletion. A dead-code detector has no way to output "this is old, unreferenced
by anything in the repository, and must stay" — the shape of its output is a list of removal
candidates. Codebase Zero's most valuable outputs are sometimes the artifacts it takes *off* that
list, with the reason written down.

INVEST goes further and inverts the recommendation: this subsystem is the most expensive,
highest-churn, most-feared thing in the repository, and the correct action is to spend *more*
engineering here. No code-minimization pass produces that output, because its objective function
cannot represent it.

**2. Evidence must come from outside the code, and outside evidence beats inside evidence.**

The worked audits are built around cases where every in-repository signal points the wrong way:

- A payload emitter untouched for three years, duplicated by a newer implementation, worst
  maintainability score in its package — and still a live customer contract, provable only from rows
  in a table and a documented public format.
- A guard whose duplicate-detected counter has not incremented in fourteen months — which is what a
  working guard looks like, not an idle one.
- An unreferenced module that a per-deployment config value might select, where the config is not in
  the repository at all.

In each, a reference-counting tool has all the evidence it can see and reaches the expensive answer.
The distinguishing move is knowing which evidence the repository *cannot* contain, and treating its
absence as a blocker rather than as a clean result.

**3. The question is about the requirement, not the code.**

Step 2 of the procedure asks what requirement caused the artifact to exist and whether that
requirement is still valid. That routes through `git log --diff-filter=A`, commit messages, and
linked tickets — reading history for *intent*, not for churn statistics. An artifact whose original
requirement was explicitly time-boxed and whose box has closed is a different case from an artifact
whose reason cannot be found, even when their reference counts are identical: the first is DELETE,
the second is at most DEFER CLEANUP.

Static analysis cannot make that distinction, because the distinction is not in the code.

**4. Mission-relative judgement, and the refusal to use size or age as a proxy.**

The audit begins by stating what the system must do well. Every verdict is relative to that
sentence. Three explicit anti-heuristics follow from it: age is not irrelevance, churn is not value,
and no traffic is not no purpose. Maintenance-cost ranking — the metric that puts a matching engine
first for cleanup — is precisely the metric this skill is built to distrust.

**5. Deletion is a hypothesis with a blast radius and a required verification.**

Every non-trivial verdict must name what a change reaches, including what could not be enumerated,
and the specific check that would fail if the removal were wrong. The audit is explicitly told that
"run the full test suite" is only an answer after confirming the suite covers the artifact — a green
suite that never exercised the deleted path proves the path was untested, not unused.

## Where the honest answer is "use the other tool"

Use a static analyzer, not this, when:

- You want exhaustive coverage of a whole repository. This skill audits the artifacts you point it
  at; it does not sweep.
- Your question is statically decidable — unreferenced symbols, unused imports, unreachable
  branches, unused dependencies. Determinism wins.
- You want it to run in CI on every commit. This produces prose for a human to argue with, which is
  the wrong output shape for a gate.

Use a code-minimization or refactoring pass, not this, when:

- The code has already been decided on and the question is purely about implementation quality.
- You want many small local improvements rather than a handful of existence decisions.

**The most efficient combination is both, in order:** run the analyzer to produce candidates, then
audit the candidates that are not obviously safe. The analyzer answers "is this referenced" cheaply
and definitively. This skill answers "should this exist", which is the question that remains after a
candidate list arrives — and it is the question that decides the three or four artifacts on that
list whose removal would be expensive.

## What this skill deliberately is not

- Not a static analyzer, and not competitive with one on coverage or determinism.
- Not a dependency-graph engine. It uses the search tools already present.
- Not a service, daemon, MCP server, database, or dashboard. It is Markdown.
- Not an automatic mass-deletion pass. The default is audit only, and the apply path is one
  hypothesis at a time.
- Not a LOC-reduction metric. If line count is what you are optimizing, the INVEST verdict will look
  like a bug rather than the point.

## Relationship to Requirement Zero

Same repository, adjacent question, different stage.

| | Requirement Zero | Codebase Zero |
|---|---|---|
| Question | Should this be built? | Does this still deserve to exist? |
| Stage | Before implementation | After accumulation |
| Input | A request, and the evidence behind it | An artifact, and the evidence around it |
| Cost of a wrong "remove" | Work not done that should have been | Something already relied upon breaks |
| Verdicts | DELETE, REDUCE, DEFER, BUILD, BUILD HARD | DELETE, CONSOLIDATE, SIMPLIFY, DEFER CLEANUP, KEEP, INVEST |

The doctrine they share is the evidence asymmetry: absent evidence lowers confidence in
*speculative* scope, and does not license removing a *protective* constraint. It matters more here,
because the artifact under audit is already load-bearing for someone. Requirement Zero's BUILD HARD
and Codebase Zero's INVEST are the same refusal to treat minimalism as the objective, applied at
two different stages.

## Evidence for the claims in this document

The behavioural claims above are argued, and partly measured. The evaluation in
[../../eval/codebase-zero/](../../eval/codebase-zero/) tests the six verdicts against a plain
coding-agent baseline on seven constructed cases, three of which guard against removing something
load-bearing. Read [its results](../../eval/codebase-zero/results/) for what was actually observed,
including where the skill arm showed no advantage.

Two things that suite does **not** establish, stated plainly because the differentiation argument
above would be stronger if they did:

- **No comparison against a specific third-party audit tool was run.** Installing and running an
  external tool was ruled out rather than done, so every comparison in this document is an argument
  about what those tools' output shape can and cannot represent — not a measured head-to-head. A
  reader who wants that comparison should run it; the argument here is falsifiable, which is the most
  that can be claimed for it.
- **The evidence-gathering half of the skill is untested.** The evaluation gives the agent no tools,
  so the searches this document treats as the distinguishing move are pre-supplied by the case
  bodies rather than performed. What is measured is judgement on a fixed evidence set.
