# Codebase Zero evaluation suite

Codebase Zero is a Markdown skill that makes a coding agent decide whether an artifact that
*already exists* still deserves to exist, before anything is changed. It commits to one of six
verdicts: **DELETE**, **CONSOLIDATE**, **SIMPLIFY**, **DEFER CLEANUP**, **KEEP**, **INVEST**. See
[../../skills/codebase-zero/SKILL.md](../../skills/codebase-zero/SKILL.md).

This directory answers one question:

> Does loading the skill change the agent's audit decision in the intended direction — removing
> scope that no longer earns its place — **without** deleting the artifacts that are load-bearing?

Both halves matter equally, and the second half is the harder one for an audit skill. A skill that
answers DELETE to everything would score well on "removes scope" and would be actively dangerous
pointed at a real repository. So three of the seven cases are ones where the correct answer is *do
not remove it*: a three-year-untouched file that is still a live customer contract, the most
expensive and highest-churn subsystem in a codebase, and a protective mechanism whose counter has
not incremented in fourteen months.

This suite shares its harness with the Requirement Zero suite — one script, two profiles. The
design decisions that apply to both (the two arms, `--safe-mode` and `--tools ""` isolation, verdict
extraction, why the baseline is deliberately strong, why token figures are not a saving) are
documented once in [../README.md](../README.md) and are not repeated here. Read that first. This
file covers only what is specific to auditing existing code.

Read the results, not this file, for findings: [results/](results/).

## Running it

```bash
python3 eval/run_eval.py --profile codebase-zero
```

Seven cases × 2 arms × 3 runs = 42 CLI calls. For one cheap pair:

```bash
python3 eval/run_eval.py --profile codebase-zero --runs 1 --case 01
```

Output goes to `eval/codebase-zero/results/<UTC-date>-<model>.json`. Runs made with any filter flag
are suffixed `-partial`. The harness prints an aggregate table and writes no prose: the summary in
`results/*.md` is hand-written from the JSON, so no narrative claim exists that a person did not
check against the data.

`--self-test` covers both profiles' vocabularies in one pass and makes no API calls.

## What is specific to this profile

**A different vocabulary, and one dangerous collision.** `DEFER CLEANUP` and `DELETE` both begin
with D, and `DEFER CLEANUP` contains `DEFER`, which is a verdict in the *other* profile. The
harness matches longest-first within the active profile's vocabulary, and `--self-test` pins
`DEFER CLEANUP` against degrading to `DEFER` under the emphasis and hyphenation noise that models
actually produce.

**A different definition of the dangerous error.** In the Requirement Zero suite a false rejection
is refusing work that should be built. Here it is the mirror image: reaching DELETE, CONSOLIDATE, or
SIMPLIFY on a case whose expected verdict is KEEP or INVEST — that is, recommending the removal or
reduction of something the case establishes as load-bearing. The harness's `false_rejections` count
is defined per profile for exactly this reason.

**Three guard cases, not one.** Cases 04, 05, and 07 each carry a `guard:` key, and a scope-losing
verdict on any of them raises the harness's `*** GUARD FAILED ***` banner. They guard three
different failure modes:

| Guard | Case | The failure it catches |
|---|---|---|
| `compatibility-contract-not-deleted` | 04 | Deleting a live contract because the file looks abandoned |
| `mission-critical-subsystem-not-simplified-away` | 05 | Recommending simplification of the subsystem where the mission actually lives |
| `protective-constraint-not-deleted` | 07 | Removing a protection because it has never fired |

Guard cases are selected by their frontmatter key, not by filename number, so renumbering the corpus
cannot silently switch the guards off.

## Cases

Seven files in [cases/](cases/), covering every category the ticket requires. Frontmatter carries the
ground truth; the body carries the artifact as it would actually present itself plus the evidence an
engineer would have gathered.

**The body never states or hints at the answer.** No verdict word, no reasoning, no "this is still
needed". Where a case has a decisive argument, the body supplies the *situation* that argument
operates on and not the argument — case 07 gives the fourteen-month quiet counter and the retrying
client SDK, and never says that a quiet guard may be a working one.

| Case | Expected | Category | Worked audit |
|---|---|---|---|
| `01-legacy-csv-export-path.md` | DELETE | truly obsolete subsystem | [delete-legacy-csv-exporter.md](../../skills/codebase-zero/examples/delete-legacy-csv-exporter.md) |
| `02-three-billing-http-clients.md` | CONSOLIDATE | duplicate implementations | [consolidate-three-http-clients.md](../../skills/codebase-zero/examples/consolidate-three-http-clients.md) |
| `03-notification-provider-abstraction.md` | SIMPLIFY | single-use abstraction | [simplify-notification-provider-abstraction.md](../../skills/codebase-zero/examples/simplify-notification-provider-abstraction.md) |
| `04-v1-webhook-payload.md` | KEEP | old-looking real compatibility contract | [keep-v1-webhook-payload-shape.md](../../skills/codebase-zero/examples/keep-v1-webhook-payload-shape.md) |
| `05-order-matching-engine.md` | INVEST | core bottleneck deserving more investment | [invest-matching-engine.md](../../skills/codebase-zero/examples/invest-matching-engine.md) |
| `06-orphaned-report-builder.md` | DEFER CLEANUP | insufficient evidence | [defer-cleanup-report-builder.md](../../skills/codebase-zero/examples/defer-cleanup-report-builder.md) |
| `07-payment-idempotency-guard.md` | KEEP | protective mechanism not casually removed | [keep-idempotency-replay-guard.md](../../skills/codebase-zero/examples/keep-idempotency-replay-guard.md) |

Each case's `example:` path is checked to resolve on disk at load time, so the reasoning behind every
expected verdict is one click away and cannot silently rot.

### Why cases 02 and 03 are the ambiguous pair

CONSOLIDATE and SIMPLIFY are adjacent, and the boundary is arithmetic: more than one artifact doing
one job is CONSOLIDATE; one artifact carrying structure nothing uses is SIMPLIFY. Case 02 has three
clients and case 03 has one implementation behind four layers of indirection, so the ground truth is
defensible — but an arm that answers SIMPLIFY on 02 has not made a serious error, it has chosen the
adjacent label. **The match metric cannot see that distinction**, which is one reason match rate is
a noisy proxy here. The results write-up reports label movement between these two separately from
movement into or out of the removal-versus-retention decision, because only the latter is
consequential.

### Why case 06 is not simply DELETE

Everything visible in the repository supports deleting the orphaned module: no references, no tests,
no ticket, a "wip" commit message, an absent author. The one fact that blocks it is that the
package selects its builder through a per-deployment config value that this repository does not
contain. So "I found no caller" and "there is no caller" come apart, and the honest verdict is
DEFER CLEANUP with the two missing pieces of evidence named.

This is the case most likely to be scored "wrong" for a defensible reason, and it is deliberately
the hardest of the seven. An arm that answers DELETE here has demonstrated exactly the failure mode
the skill exists to prevent — but it has demonstrated it on a case where the wrong answer is *cheap*
to reach and looks thorough.

## Limitations

Every limitation in [../README.md](../README.md#limitations) applies unchanged: tiny N, non-
determinism, a single model, no implementation arm, prompt sensitivity, a strong baseline that
compresses the measured difference, caching contamination of token figures, ground truth that is
this repository's own opinion, and match rate grading the label rather than the decision. Read them
there.

Three limitations are specific to this profile:

1. **The cases are constructed, not sampled from real repositories.** Every fact in a case body was
   written to be internally consistent and to withhold the answer. Real audits arrive with messier,
   more contradictory evidence, and with the option to run one more search — which these cases
   deliberately deny, since the harness gives the agent no tools. What is measured is judgement on a
   fixed evidence set, not evidence-gathering skill.

2. **No evidence-gathering is measured at all.** `--tools ""` means the agent cannot run `rg`, read
   `git log`, or check a config file. Half of what the skill actually specifies — which searches to
   run, in what order, and when to stop — is therefore untested by this suite. The cases pre-supply
   the evidence a competent search would have found. Testing the search behaviour would need an arm
   with tools and a real repository, which is a much larger and noisier experiment than this one.

3. **Seven constructed cases cannot show that the skill is safe pointed at a real codebase.** Three
   guards passing is a floor, not an assurance. Nothing here substitutes for the skill's own
   audit-only default and its one-hypothesis-per-PR apply gates.

## Adding a case

Add `cases/NN-slug.md` with frontmatter `id`, `expected_verdict` (one of the six), `case_type`,
`example` (a path that resolves), and optionally `guard`. Keep every trace of the answer out of the
body, including the reasoning and not just the verdict word. Then run
`python3 eval/run_eval.py --profile codebase-zero --runs 1 --case NN` to check it loads and parses,
and add the worked reasoning to
[../../skills/codebase-zero/examples/](../../skills/codebase-zero/examples/) so the expected verdict
is defensible to a reader.
