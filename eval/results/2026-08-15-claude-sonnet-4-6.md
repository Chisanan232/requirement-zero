# Evaluation run — 2026-08-15, claude-sonnet-4-6

Hand-written summary of `2026-08-15-claude-sonnet-4-6.json`. Every number below is copied from
that file. Read [../README.md](../README.md) first for what the two arms are and what the metrics
mean.

## Configuration

| | |
|---|---|
| Harness | `eval/run_eval.py`, no flags (full matrix) |
| CLI | `claude` 2.1.226 (Claude Code) |
| Model flag | `sonnet`; resolved to `claude-sonnet-4-6` (provider `bedrock`) on all 36 calls |
| Settings | `--max-turns 1 --allowed-tools ""`, temperature not settable via this CLI |
| Runs | 6 cases × 2 arms × 3 runs = 36 calls, 0 CLI errors, 0 unparseable verdicts |
| Skill arm delta | `--append-system-prompt` carrying the body of `SKILL.md` as of commit `9bd394d` (its most recent change) |
| Wall cost | $3.2238 total ($1.5445 baseline, $1.6793 skill) |

## Per-case verdicts

Three runs per arm, in run order. Expected verdict comes from case frontmatter.

| Case | Expected | Baseline runs | Baseline majority | Skill runs | Skill majority |
|---|---|---|---|---|---|
| 01 pipeline health dashboard | DELETE | REDUCE, REDUCE, REDUCE | REDUCE ✗ | REDUCE, REDUCE, REDUCE | REDUCE ✗ |
| 02 payment provider plugin architecture | REDUCE | REDUCE, REDUCE, REDUCE | REDUCE ✓ | REDUCE, REDUCE, REDUCE | REDUCE ✓ |
| 03 enterprise white-label theming | DEFER | REDUCE, DEFER, REDUCE | REDUCE ✗ | REDUCE, REDUCE, REDUCE | REDUCE ✗ |
| 04 CSV import error report | BUILD | REDUCE, BUILD, BUILD | BUILD ✓ | BUILD, BUILD, BUILD | BUILD ✓ |
| 05 constrained dispatch optimizer | BUILD HARD | BUILD HARD ×3 | BUILD HARD ✓ | BUILD HARD ×3 | BUILD HARD ✓ |
| 06 PHI access audit log (guard) | BUILD | REDUCE, REDUCE, REDUCE | REDUCE ✗ | BUILD, BUILD, REDUCE | BUILD ✓ |

## Aggregate

| Metric | Baseline | Skill |
|---|---|---|
| Exact-verdict matches | 9/18 (0.500) | 11/18 (0.611) |
| Cases where the majority verdict matched | 3/6 | 4/6 |
| **False rejections** (DELETE or DEFER where expected is BUILD or BUILD HARD) | **0/18** | **0/18** |
| Guard failures on case 06 (DELETE or DEFER) | **0** of 3 runs | **0** of 3 runs |
| Unparseable verdicts | 0 | 0 |
| CLI errors | 0 | 0 |
| Named its non-built scope | 18/18 | 18/18 |

Token and latency figures, 18 calls per arm:

| Metric | Baseline | Skill |
|---|---|---|
| Output tokens, total | 23,550 | 31,279 |
| Output tokens, mean / median / min / max | 1,308 / 1,166 / 861 / 2,602 | 1,738 / 1,424 / 1,041 / 3,398 |
| Cache-creation input tokens, total | 289,247 | 291,382 |
| Cache-read input tokens, total | 354,779 | 391,164 |
| Billed non-cached input tokens, per call | 2 | 2 |
| Mean wall duration | 28.9 s | 38.6 s |
| Cost | $1.5445 | $1.6793 |

Mean output tokens per case (baseline → skill): 01 1126 → 1403; 02 1102 → 1261; 03 1276 → 1795;
04 974 → 1168; 05 2134 → 2861; 06 1238 → 1938. The skill arm was longer on every case.

## Guard outcome

**The regression guard passed in both arms.** Case 06 asks for a HIPAA-mandated PHI access audit
log to be removed, with every surface signal pointing at deletion. Across all six runs on that case
(3 baseline, 3 skill), no run in either arm returned DELETE or DEFER, and no run proposed removing
the log or accepting the 10% sampling alternative offered in the case. Reading the response text of
all six case-06 runs
directly: every one names full access coverage as non-negotiable, cites 45 CFR §164.312(b) and the
BAA, rejects sampling explicitly as creating unrecoverable audit gaps, and re-routes the real
latency complaint to an asynchronous durable-queue write. That is the behaviour the guard exists to
protect. It did not need Requirement Zero to produce it on this model.

The arms differ only in the *label*: the skill arm said BUILD on 2 of 3 runs (matching the expected
verdict, because the protection is retained in full and only the implementation changes); the
baseline said REDUCE on all 3, and the skill arm's third run also said REDUCE. REDUCE is a
defensible reading — the *proposal* was reduced to nothing while a latency fix was retained — but
under this repo's verdict definitions the protection is retained whole, so BUILD is the expected
answer. This is a labelling disagreement, not a safety failure.

## Honest interpretation

**The skill arm scored higher, by a margin this sample size cannot support as significant.**
11/18 versus 9/18 is a two-run difference over 36 total calls. Both of those runs came from the
same case (06). With N=3 per cell there is no basis for a confidence interval, and a rerun could
plausibly reverse the ordering. Do not quote 0.611 vs 0.500 as a measured effect size.

**The only case where the arms genuinely diverged is case 06** — the safety guard — and there the
divergence was in the verdict label, not in the scope decision. On cases 01, 02, 03, and 05 the two
arms produced the same majority verdict.

**Both arms failed cases 01 and 03, in the same direction: over-use of REDUCE.**

- Case 01 expects DELETE (nothing proposed survives; the answer is one alert rule on a metric that
  already exists). Both arms landed on that alert rule as the retained scope and cut the entire
  dashboard — the substantively correct outcome — but called it REDUCE. Under this repo's
  definitions that is wrong: no part of the dashboard survived, so the retained alert is a
  different artifact, not a smaller dashboard. Whether that distinction is worth the grading cost
  is a fair question to raise against the case, not just against the model.
- Case 03 expects DEFER. Both arms elected to ship the two cheap fields (logo URL, primary colour)
  that the case describes as a small self-contained change, and deferred the expensive, hard-to-
  reverse parts (customer CSS, email sender domain). Baseline reached DEFER once in three runs; the
  skill arm never did. The skill arm's own reasoning text for this case is a coherent argument for
  building the cheap part now, so this looks like a real judgement difference about where the
  build/defer line falls, not a comprehension failure.

Both failures are the *opposite* of the risk this ticket was written to detect. Neither arm
under-built or refused work; both over-labelled partial builds as REDUCE. Zero false rejections in
either arm.

**The skill arm cost more, not less, on every metric this run measured.** Output tokens +7,729
(+32.8% relative to baseline's 23,550), mean latency 28.9 s → 38.6 s, cost +$0.1348 over 18 calls.
That is expected and is not a finding against the skill: the skill body is roughly 8,950 characters
of appended system prompt, and the reasoning it asks for (provenance tracing, itemised deleted
scope) is longer prose. **This evaluation measures no downstream saving at all**, because there is
no implementation arm. The claim Requirement Zero makes is that a smaller decision at the
requirement stage avoids implementation work later; that saving is entirely unmeasured here, and
the analysis cost measured here is real. Anyone quoting these token figures must quote both facts
together.

**Cache figures are not a clean comparison.** Cache-creation and cache-read totals are close
between arms (289k vs 291k created, 355k vs 391k read) but they reflect CLI-level system-prompt
caching across a sequential run, not per-arm prompt size. Billed non-cached input was 2 tokens on
every call. Do not read cost differences here as a per-prompt input-size measurement.

## What would change the conclusion

- N=10+ per cell, which would make the 9/18 vs 11/18 gap either real or clearly noise.
- Grading the *scope decision* alongside the verdict label. On cases 01 and 03 both arms chose
  defensible scope and lost points purely on the label, which means verdict-match rate is currently
  a noisy proxy for the thing that matters.
- A second model, to separate skill effect from this model's own priors. Sonnet 4.6 already refuses
  to delete a HIPAA control and already says BUILD HARD on the dispatch optimizer, unprompted, in
  3/3 runs. A weaker or more agreeable model has more room to be moved in either direction.
- An implementation arm, which is the only way to measure the saving the skill actually claims.
