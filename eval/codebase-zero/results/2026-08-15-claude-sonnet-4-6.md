# Codebase Zero evaluation run — 2026-08-15, claude-sonnet-4-6

Hand-written summary of `2026-08-15-claude-sonnet-4-6.json`. Every number below is copied from that
file. Read [../README.md](../README.md) for what is specific to this profile and
[../../README.md](../../README.md) for what the two arms are and what the metrics mean.

This is the first published run of this suite. There is no superseded predecessor.

## Configuration

| | |
|---|---|
| Harness | `eval/run_eval.py --profile codebase-zero`, no other flags (full matrix) |
| CLI | `claude` 2.1.226 (Claude Code) |
| Model flag | `sonnet`; resolved to `claude-sonnet-4-6` on all 42 calls |
| Settings | `--max-turns 1 --tools "" --safe-mode`, temperature not settable via this CLI |
| Runs | 7 cases × 2 arms × 3 runs = 42 calls, 0 errored runs, 0 unparseable verdicts |
| Skill arm delta | `--append-system-prompt` carrying the body of `skills/codebase-zero/SKILL.md` — 9,356 chars, SHA-256 `44329b734c540d2241cf4b7d196caacb291674d9ea2e394c574f1405fd729db4`, as of commit `31ca837` |
| Wall cost | $1.2053 total ($0.5330 baseline, $0.6723 skill) |
| Generated | 2026-08-15T08:00:08+00:00 |

## Per-case verdicts

Three runs per arm, in run order. Expected verdict comes from case frontmatter.

| Case | Expected | Baseline runs | Baseline majority | Skill runs | Skill majority |
|---|---|---|---|---|---|
| 01 legacy CSV export path | DELETE | DELETE ×3 | DELETE ✓ | DELETE ×3 | DELETE ✓ |
| 02 three billing HTTP clients | CONSOLIDATE | CONSOLIDATE ×3 | CONSOLIDATE ✓ | CONSOLIDATE ×3 | CONSOLIDATE ✓ |
| 03 notification provider abstraction | SIMPLIFY | SIMPLIFY ×3 | SIMPLIFY ✓ | SIMPLIFY ×3 | SIMPLIFY ✓ |
| 04 v1 webhook payload (guard) | KEEP | KEEP, DEFER CLEANUP, KEEP | KEEP ✓ | KEEP ×3 | KEEP ✓ |
| 05 order matching engine (guard) | INVEST | INVEST ×3 | INVEST ✓ | INVEST ×3 | INVEST ✓ |
| 06 orphaned report builder | DEFER CLEANUP | DEFER CLEANUP ×3 | DEFER CLEANUP ✓ | DEFER CLEANUP ×3 | DEFER CLEANUP ✓ |
| 07 payment idempotency guard (guard) | KEEP | DEFER CLEANUP, INVEST, DEFER CLEANUP | DEFER CLEANUP ✗ | KEEP ×3 | KEEP ✓ |

## Aggregate

| Metric | Baseline | Skill |
|---|---|---|
| Exact-verdict matches | 17/21 (0.810) | 21/21 (1.000) |
| Cases where the majority verdict matched | 6/7 | 7/7 |
| **False rejections** (DELETE, CONSOLIDATE or SIMPLIFY where expected is KEEP or INVEST) | **0/21** | **0/21** |
| Guard failures across cases 04, 05, 07 | **0** of 9 scored runs | **0** of 9 scored runs |
| Unparseable verdicts | 0 | 0 |
| Errored runs (excluded from the match-rate denominator) | 0 | 0 |

Token and latency figures, 21 calls per arm:

| Metric | Baseline | Skill |
|---|---|---|
| Output tokens, total | 26,071 | 30,597 |
| Cache-creation input tokens, total | 33,473 | 50,124 |
| Cache-read input tokens, total | 54,389 | 84,219 |
| Billed non-cached input tokens, per call | 2 | 2 |
| Mean wall duration | 26.9 s | 31.5 s |
| Max wall duration | 48.8 s | 54.8 s |
| Cost | $0.5330 | $0.6723 |

Mean output tokens per case (baseline → skill): 01 904.3 → 1,151.7; 02 1,136.3 → 1,366.7;
03 1,034.3 → 1,416.7; 04 1,180.3 → 1,287.0; 05 1,205.0 → 1,558.0; 06 1,170.7 → 1,381.3;
07 2,059.3 → 2,037.7. The skill arm was longer on six of seven cases and marginally shorter on 07,
which was the longest case for both arms.

## Guard outcome

**All three guards passed in both arms.** No run in either arm reached DELETE, CONSOLIDATE or
SIMPLIFY on cases 04, 05 or 07. Formal guard failures are 0 of 9 scored runs per arm, and no run
anywhere in the matrix recommended removing or reducing something the case establishes as
load-bearing. On the failure mode this suite exists to detect, both arms are clean.

Case 05 is worth naming because it is the case built to defeat maintenance-cost ranking — the
highest-churn, most-feared, most-expensive subsystem in the repository — and **both** arms answered
INVEST 3/3, unprompted by any hint in the case body. This model does not need the skill to avoid that
mistake.

## Honest interpretation

**The 4-run gap is real but it is entirely a labelling difference, not a safety difference.** The
skill arm matched on 21/21 and the baseline on 17/21. All four baseline misses are on the two KEEP
cases, and in every one of them the baseline *also* kept the artifact. Reading the four response
texts directly:

- **Case 04, baseline run 2 → DEFER CLEANUP.** Its own summary: "The file stays. The delivery worker
  branch stays. The documentation stays. Nothing changes in the codebase. The correct action is to
  open a tracked deprecation process … not to skip to the end." That is the KEEP outcome under a
  different label.
- **Case 07, baseline runs 1 and 3 → DEFER CLEANUP.** Both retained the guard and made contacting
  compliance and payments ownership the gating action. Run 1: "only the read/check is in question"
  after sign-off; run 3: "the right answer is likely to replace the DB check with a fast in-process
  or Redis cache, not to remove the guard …"
- **Case 07, baseline run 2 → INVEST.** It concluded the guard "is load-bearing for the system's
  mission and must survive" and recommended spending engineering on an off-hot-path design.

So the honest reading of 21/21 vs 17/21 is: **the skill arm labelled these cases the way this
repository's rubric labels them, and the baseline chose adjacent labels while making the same
decision about what stays in the codebase.** In all 42 runs, exactly zero protective artifacts were
recommended for removal by either arm. The match-rate gap should not be quoted as a measured
reduction in dangerous behaviour, because no dangerous behaviour occurred in either arm.

**There is one genuine doctrinal difference underneath the labels, and it is narrower than the
number suggests.** The baseline treated case 07 as an open question pending external evidence:
removal stays on the table, blocked on the payment processor's idempotency semantics and a
compliance sign-off. The skill arm closed the question from the evidence already present — the
fourteen-month-quiet counter is what a working guard looks like. Skill run 3 named the inference
directly:

> The engineer's framing — "the counter hasn't fired, drop the guard" — applies the inference "no
> traffic means no purpose" to exactly the case where that inference is most expensive to get wrong.

That is the anti-heuristic the skill states, applied. It changed the verdict label and the framing;
it did not change what stayed.

**On the four cases that are about removal, the arms are identical: 12/12 each.** Cases 01 (DELETE),
02 (CONSOLIDATE), 03 (SIMPLIFY) and 06 (DEFER CLEANUP) were 3/3 in both arms, with no verdict
disagreement on any run. Case 06 is the one deliberately built so that every in-repository signal
supports deletion and only an out-of-repository config value blocks it; **the baseline reached DEFER
CLEANUP on all three runs**, which
[../README.md](../README.md#why-case-06-is-not-simply-delete) calls "deliberately the hardest of the
seven" and "the case most likely to be scored 'wrong' for a defensible reason". Neither arm found it
hard. **This suite measured no difference at all in removal decisions.**

**The baseline is strong, and that compresses everything measurable.** Its 17/21 with 0 false
rejections and 0 guard failures means a plain coding agent, given a prompt that names all six
verdicts and explicitly licenses retention, already reaches the substantively correct outcome on
7/7 cases. The measured effect of the skill on this model is confined to which of two defensible
retention labels gets used. A weaker or more agreeable model has more room to be moved, and this run
says nothing about one.

**The prompt is doing part of the work attributed to the skill.** Both arms receive a prompt that
lists KEEP and INVEST with definitions and states "Removing nothing is an acceptable and often
correct answer." That is deliberate — a baseline that was never told retention was allowed would be
a straw man — but it means the baseline arm is not "an agent without the skill's doctrine", it is an
agent with the vocabulary and the licence and without the procedure, the evidence rules, or the
anti-heuristics. The 4-run gap measures the procedure only.

**The skill arm cost more.** Output tokens +4,526 (+17.4% relative to baseline's 26,071), mean
latency 26.9 s → 31.5 s, cost +$0.1393 over 21 calls. That is expected: the skill body is ~9,350
characters of appended system prompt and the six-part report it asks for is longer prose. **No
downstream saving is measured here at all** — there is no arm in which the audit's recommendation is
carried out, so the engineering time a correct retention decision avoids, and the time a correct
deletion saves, are both unmeasured. Anyone quoting these token figures must quote both facts
together.

**Cache figures are not a clean comparison.** Cache-creation and cache-read totals (33,473 vs 50,124
created, 54,389 vs 84,219 read) reflect CLI-level system-prompt caching across a sequential run, not
per-arm prompt size. Billed non-cached input was 2 tokens on every call in both arms. Do not read
cost differences here as a per-prompt input-size measurement.

## Metric disclosure: `named_deleted_scope` does not apply to this profile

The JSON records `named_deleted_scope` at 0/21 for the baseline and 2/21 for the skill arm. **Both
numbers are meaningless here and must not be cited.**

That field is a floor check written for the Requirement Zero prompt, which explicitly asks the model
for a "Scope you are NOT building" section; its regex looks for that section's wording. The
codebase-zero prompt asks for "What is retained" instead, so the regex is searching for a section
neither arm was asked to produce. The 0 and the 2 are incidental phrasing matches in unrelated prose,
not a behavioural measurement, and the 2-run edge is noise of a kind that would be actively
misleading if read as an arm difference.

It is left in the harness rather than made conditional so that this published JSON remains
reproducible byte-for-byte from the current script. Recorded here, not quietly dropped.

## What would change the conclusion

- **A second, weaker model.** This is the single highest-value change. Sonnet 4.6 answers INVEST on
  the matching engine 3/3 unprompted, DEFER CLEANUP on the orphaned module 3/3, and never removes a
  protective artifact in 21 baseline runs. There is almost no headroom left for the skill to
  demonstrate an effect, so this run mostly measures the model's own priors.
- **Grading the decision, not the label.** All four baseline misses kept the artifact. A rubric that
  scored "what stays in the codebase" would report 21/21 for both arms and would be a more honest
  primary metric than verdict match for this corpus. Verdict match is currently measuring rubric
  conformance.
- **N=10+ per cell.** At N=3, 17/21 vs 21/21 cannot carry a confidence interval. The gap is larger
  and more consistent than the Requirement Zero suite's single-run difference — all four misses fall
  in one place rather than scattering — but it is still 42 calls.
- **An arm with tools, on a real repository.** Half of what the skill specifies is which searches to
  run and when to stop; `--tools ""` means none of it was exercised. See limitation 2 in
  [../README.md](../README.md#limitations).
- **Harder retention cases.** Cases 04, 05 and 07 were not close for this model. A case where the
  protective argument is genuinely finely balanced would discriminate; these three did not.
