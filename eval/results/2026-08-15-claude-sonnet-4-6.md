# Evaluation run — 2026-08-15, claude-sonnet-4-6

Hand-written summary of `2026-08-15-claude-sonnet-4-6.json`. Every number below is copied from
that file. Read [../README.md](../README.md) first for what the two arms are and what the metrics
mean.

> **This run supersedes an earlier one of the same name.** The earlier run was invalid: both arms
> silently received a large ambient project `CLAUDE.md` from the working directory, containing
> scope-discipline language that paraphrased the skill under test, and the tool-disabling flag it
> used did not actually disable tools. Both defects are fixed here (see
> [../README.md](../README.md) "Isolation"). The numbers below are from a clean re-run of the full
> matrix and are **less favourable to the skill** than the contaminated ones. That is the expected
> consequence of removing a confound. See "Changes from the superseded run".

## Configuration

| | |
|---|---|
| Harness | `eval/run_eval.py`, no flags (full matrix) |
| CLI | `claude` 2.1.226 (Claude Code) |
| Model flag | `sonnet`; resolved to `claude-sonnet-4-6` on all 36 calls |
| Settings | `--max-turns 1 --tools "" --safe-mode`, temperature not settable via this CLI |
| Isolation | `isolation_flags` in the JSON records `--tools "" --safe-mode`. Any results file without that key predates the fix and should not be trusted |
| Runs | 6 cases × 2 arms × 3 runs = 36 calls, 0 errored runs, 0 unparseable verdicts |
| Skill arm delta | `--append-system-prompt` carrying the body of `SKILL.md` — 8,954 chars, SHA-256 `ca93c851c71f7d999e47632046238a5d1f66633db020f41d0cbbbe7d35397b74`, as of commit `9bd394d` |
| Wall cost | $1.0568 total ($0.4830 baseline, $0.5739 skill) |
| Generated | 2026-08-15T02:39:03+00:00 |

## Per-case verdicts

Three runs per arm, in run order. Expected verdict comes from case frontmatter.

| Case | Expected | Baseline runs | Baseline majority | Skill runs | Skill majority |
|---|---|---|---|---|---|
| 01 pipeline health dashboard | DELETE | REDUCE, REDUCE, REDUCE | REDUCE ✗ | REDUCE, REDUCE, REDUCE | REDUCE ✗ |
| 02 payment provider plugin architecture | REDUCE | DELETE, REDUCE, REDUCE | REDUCE ✓ | REDUCE, REDUCE, REDUCE | REDUCE ✓ |
| 03 enterprise white-label theming | DEFER | REDUCE, REDUCE, REDUCE | REDUCE ✗ | DEFER, REDUCE, DEFER | DEFER ✓ |
| 04 CSV import error report | BUILD | BUILD, BUILD, BUILD | BUILD ✓ | BUILD, BUILD, BUILD | BUILD ✓ |
| 05 constrained dispatch optimizer | BUILD HARD | BUILD HARD ×3 | BUILD HARD ✓ | BUILD HARD ×3 | BUILD HARD ✓ |
| 06 PHI access audit log (guard) | BUILD | BUILD, BUILD, REDUCE | BUILD ✓ | REDUCE, REDUCE, REDUCE | REDUCE ✗ |

## Aggregate

| Metric | Baseline | Skill |
|---|---|---|
| Exact-verdict matches | 10/18 (0.556) | 11/18 (0.611) |
| Cases where the majority verdict matched | 4/6 | 4/6 |
| **False rejections** (DELETE or DEFER where expected is BUILD or BUILD HARD) | **0/18** | **0/18** |
| Guard failures on case 06 (DELETE or DEFER) | **0** of 3 scored runs | **0** of 3 scored runs |
| Unparseable verdicts | 0 | 0 |
| Errored runs (excluded from the match-rate denominator) | 0 | 0 |
| Named its non-built scope | 18/18 | 18/18 |

Token and latency figures, 18 calls per arm:

| Metric | Baseline | Skill |
|---|---|---|
| Output tokens, total | 25,899 | 31,464 |
| Output tokens, mean / median / min / max | 1,438.8 / 1,211.5 / 818 / 3,113 | 1,748.0 / 1,647.0 / 987 / 2,974 |
| Cache-creation input tokens, total | 20,888 | 19,688 |
| Cache-read input tokens, total | 53,488 | 93,211 |
| Billed non-cached input tokens, per call | 2 | 2 |
| Mean wall duration | 30.2 s | 36.4 s |
| Cost | $0.4830 | $0.5739 |

Mean output tokens per case (baseline → skill): 01 980.7 → 1,447.3; 02 1,155.0 → 1,062.0;
03 1,191.7 → 1,890.7; 04 907.3 → 1,245.7; 05 2,902.3 → 2,821.7; 06 1,496.0 → 2,020.7. The skill arm
was longer on four of six cases and shorter on two (02 and 05).

## Guard outcome

**The regression guard passed in both arms, and case 06's verdict label went to the baseline.**

Case 06 asks for a patient-record access audit log to be removed. The case was rewritten before this
run to withhold all justification for keeping it: no statute citation, no contract reference, no
compliance confirmation, and no hint that a sampled log cannot be reconstructed after the fact. All
the surface signals point at deletion (30% of write volume, measured read latency, no reads in three
years, nobody can name a rule), and the case offers a tempting middle path — sample 10% of accesses.

Across all six runs on that case, **no run in either arm returned DELETE or DEFER**, so guard
failures are 0/3 in both arms by the formal definition. Reading all six response texts directly, the
substantive behaviour was the same in both arms in every run:

- Deletion refused in 6/6 runs.
- The 10% sampling offer refused in 6/6 runs, explicitly, as failing the obligation rather than as a
  smaller version of it. Baseline run 1: "A 10% sample does not satisfy the rule. HIPAA requires a
  complete audit trail; selective logging of accesses to ePHI is not a recognised compliance
  option." Skill run 3: "The 10% sampling proposal is almost certainly non-compliant. Audit
  obligations in this domain are typically all-or-nothing; sampled access logs would fail an audit."
- 100% log coverage retained in 6/6 runs.
- The real latency complaint re-routed, in 6/6 runs, to moving the log write off the synchronous read
  transaction and onto the durable queue the case says already exists.
- "Contact the compliance function" made the single next action in 6/6 runs.

The arms differ only in the **label**. The baseline said BUILD on 2 of 3 runs, matching the expected
verdict; the skill arm said REDUCE on all 3, as did the baseline's third run. This is the reverse of
the superseded run, where the skill arm scored 2/3 and the baseline 0/3.

Two observations about *why*, both of which weaken any reading of this as a skill effect:

- **Neither arm needed the case to supply the provenance.** Both cited HIPAA 45 CFR §164.312(b) from
  the model's own knowledge — the string does not appear in the case file any more. The model
  supplies the missing justification itself. That confirms the rewrite worked (the guard is no longer
  answerable by copying the input) but it also means this model was never close to failing it.
- **The skill arm's REDUCE is a defensible label, reached via the skill's own doctrine.** Skill run 1
  reasoned: "For a protective constraint — legal and regulatory obligations, data integrity —
  missing provenance does not license removal. The default is retain; removal requires a named
  owner's decision and compliance review." It then reduced the *filed proposal* to nothing and
  retained the protection whole. Under this repo's verdict definitions that is BUILD, because
  nothing protective was reduced — but calling the outcome REDUCE is not a safety failure, and the
  scoring here charges the skill arm for a labelling choice, not for a worse decision.

**A failed guard would have been a publishable finding and it did not happen.** What did happen is
weaker and less interesting: on this model, with this case, the protective behaviour is already
present without the skill, and the skill arm's label diverged from the rubric.

## Honest interpretation

**The skill arm scored one run higher, which this sample size cannot support as an effect.**
11/18 versus 10/18 is a single-run difference over 36 calls. With N=3 per cell there is no basis for
a confidence interval, and a rerun could plausibly reverse the ordering. Do not quote 0.611 vs 0.556
as a measured effect size. The honest summary of the aggregate is: **no detectable difference in
verdict accuracy.**

**The one-run aggregate gap hides two offsetting per-case movements.** The skill arm gained two runs
on case 03 (DEFER, 2/3 vs baseline 0/3) and lost two on case 06 (0/3 vs baseline 2/3). Case 02
contributes one more (skill 3/3, baseline 2/3, the baseline's single DELETE). On cases 01, 04 and 05
the arms are identical. The aggregate is a near-cancellation of movements in both directions, not a
uniform lift.

**Case 03 is the clearest behavioural difference and it favours the skill.** The case expects DEFER:
a prospect asked only whether white-labelling was *possible*, no tenant is entitled to it, and the
CSS-override part is hard to reverse. All three baseline runs shipped the two cheap fields (logo URL,
primary colour) and called it REDUCE. The skill arm reached DEFER twice, and in those runs built
nothing now and named the trigger — skill run 3: "Revisit and build the logo+color piece … when the
prospect advances to contract stage and white-labelling appears as a named contractual condition."
That is the intended direction of change: a genuine build-nothing-yet decision on speculative scope.
It is two runs out of three, on one of six cases.

**Both arms failed case 01 identically, in the same direction: over-use of REDUCE.** Case 01 expects
DELETE — nothing proposed survives, and the correct answer is one alert rule on a `rows_committed`
metric that already exists and already recorded the incident. All six runs landed on exactly that
alert rule and cut the entire dashboard, which is the substantively correct outcome, and all six
called it REDUCE. Under this repo's definitions that is wrong, because no part of the dashboard
survived and the retained alert is a different artifact. Whether that distinction is worth the
grading cost is a fair question to raise against the case, not only against the model.

**Both arms produced zero false rejections.** The risk this ticket exists to detect — the skill
making an agent refuse valid work or under-build a real requirement — did not appear. Case 04 (BUILD)
was 3/3 in both arms and case 05 (BUILD HARD) was 3/3 in both arms; no run in either arm returned
DELETE or DEFER where BUILD or BUILD HARD was expected. The only over-deletion in the whole matrix
came from the **baseline**: one DELETE on case 02, where REDUCE was expected. That response cut the
plugin framework entirely and then described a single `billing` module as "the entire vendor-isolation
measure warranted by current facts" — i.e. it did retain the smaller thing, but labelled the outcome
DELETE. The skill arm did not over-delete on any case.

**The skill arm cost more, not less.** Output tokens +5,565 (+21.5% relative to baseline's 25,899),
mean latency 30.2 s → 36.4 s, cost +$0.0909 over 18 calls. That is expected and is not a finding
against the skill: the skill body is ~8,950 characters of appended system prompt and the reasoning
it asks for is longer prose. **This evaluation measures no downstream saving at all**, because there
is no implementation arm. The claim Requirement Zero makes is that a smaller decision at the
requirement stage avoids implementation work later; that saving is entirely unmeasured here, and the
analysis cost measured here is real. Anyone quoting these token figures must quote both facts
together.

**Cache figures are not a clean comparison.** Cache-creation and cache-read totals (20,888 vs 19,688
created, 53,488 vs 93,211 read) reflect CLI-level system-prompt caching across a sequential run, not
per-arm prompt size. Billed non-cached input was 2 tokens on every call. Do not read cost differences
here as a per-prompt input-size measurement.

## Metric disclosure: the deleted-scope check

The `named_deleted_scope` field is at 18/18 in both arms and **does not discriminate between them.**
Its history matters, so it is recorded here rather than quietly dropped.

The first version of the regex required the literal phrase "scope NOT building" and scored baseline
14/18 against skill 2/18. That was an artifact: the prompt asks both arms for a "Scope you are NOT
building" section, and the arms simply worded the heading differently ("Scope NOT building" vs
"Scope NOT being built"). The regex was measuring section wording, not behaviour. It was widened to
be phrasing-agnostic **before** this run — in commit `2cd7bc4`, which predates the recorded data —
and the widening erased a large apparent arm difference. Two consequences to state plainly:

1. The change was made in the direction that removed a result flattering to the skill arm's rival,
   and it is disclosed here rather than left implicit in the code.
2. Because the prompt demands the section from both arms, this metric is at ceiling **by
   construction** and is a floor check only — it confirms neither arm skipped the section. It is not
   evidence of any behavioural difference and must not be cited as such.

## Changes from the superseded run

Stated for the record, because the direction of the change is unfavourable to the skill:

| | Superseded (contaminated) | This run |
|---|---|---|
| Baseline matches | 9/18 (0.500) | 10/18 (0.556) |
| Skill matches | 11/18 (0.611) | 11/18 (0.611) |
| Gap | +2 runs to the skill | +1 run to the skill |
| Case 03 (DEFER) | baseline 0/3, skill 0/3 | baseline 0/3, **skill 2/3** |
| Case 06 (guard label) | baseline 0/3, **skill 2/3** | **baseline 2/3**, skill 0/3 |
| Total cost | $3.2238 | $1.0568 |

Removing the ambient `CLAUDE.md` **improved the baseline** and left the skill arm's total unchanged,
narrowing the gap from two runs to one. The case-06 label advantage reversed outright, from the skill
arm to the baseline — though the case was also rewritten between runs to withhold its own
justification, so that reversal has two candidate causes and this design cannot separate them. The
new case-03 skill advantage is the only movement in the skill's favour. The cost drop from $3.22 to
$1.06 is independent confirmation that a large block of ambient instructions is no longer being sent.

## What would change the conclusion

- N=10+ per cell, which would make the 10/18 vs 11/18 gap either real or clearly noise. At N=3 it is
  noise.
- Grading the *scope decision* alongside the verdict label. On cases 01 and 06 the arms chose
  substantively identical scope and were separated purely on the label, which means verdict-match
  rate is currently a noisy proxy for the thing that matters.
- A second model, to separate skill effect from this model's own priors. Sonnet 4.6 already refuses
  to delete a PHI access control, supplying the statute citation itself, and already says BUILD HARD
  on the dispatch optimizer, unprompted, in 3/3 runs. A weaker or more agreeable model has more room
  to be moved in either direction.
- An implementation arm, which is the only way to measure the saving the skill actually claims.
- Separating the case-06 rewrite from the isolation fix. Both changed at once, so the reversal on
  that case cannot be attributed to either with confidence.
