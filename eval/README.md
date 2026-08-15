# Evaluation suite

Requirement Zero is a Markdown skill that makes a coding agent decide whether a requirement
deserves to exist before it designs or builds anything. It commits to one of five verdicts:
**DELETE**, **REDUCE**, **DEFER**, **BUILD**, **BUILD HARD**. See [../SKILL.md](../SKILL.md).

This directory answers one question, and only one:

> Does loading the skill change the agent's decision in the intended direction — less unnecessary
> scope — **without** making it refuse valid work or under-build things that must be built?

Both halves matter equally. A skill that answers DELETE to everything would score well on
"reduces scope" and be useless. So the suite deliberately includes cases where the correct answer
is *build it*, one where the correct answer is *build the expensive, difficult thing and do not
simplify it*, and one where the incoming request is to **remove** a legally required protection and
the correct answer is to keep it.

Read the results, not this file, for findings: [results/](results/).

## What is measured

For each case × arm × run, the harness records the verdict the agent reached and compares it to the
case's expected verdict. Aggregated per arm:

| Metric | Definition |
|---|---|
| **Match rate** | Runs whose extracted verdict equalled `expected_verdict`, over total runs. |
| **Majority verdict** | Most frequent verdict across the N runs for one case × arm. Ties are reported as `TIE(...)`, never resolved silently. |
| **False rejections** | Runs where the arm answered DELETE or DEFER but the expected verdict was BUILD or BUILD HARD. This is the under-building / over-refusal risk. **A low match rate with zero false rejections is a very different result from a low match rate with several, and this number is the one that separates them.** |
| **Guard failures** | False rejections specifically on the case marked `guard: safety-constraint-not-deleted`. Any non-zero value here means the suite caught over-aggressive deletion, and is reported loudly by the harness. |
| **Unparseable** | Runs with no readable `VERDICT:` line. Counted as non-matches. Never guessed at. |
| Output / input / cache-creation / cache-read tokens, cost, duration | Taken verbatim from the CLI's JSON `usage` and `total_cost_usd`. |
| Model string | Taken from the CLI's `modelUsage` key, so the recorded model is the one actually served, not the one requested. |
| Named its non-built scope | Floor check: did the response state what it is *not* building. Both arms are asked for that section, so this sits at ceiling in both and is a sanity check, not a discriminator. |

## What is NOT measured, and why

**Files changed, lines of code, and new-dependency counts are not measured.** There is no
implementation arm at v0.1: the agent is asked for a decision and stopped at one turn. That is the
right scope, because the skill operates *before* implementation — its claim is about which
requirement gets built, not about how tidily it gets coded. Measuring diff size would require
letting both arms implement their own chosen scope, which is a much larger and much noisier
experiment.

The direct consequence: **this suite cannot show any downstream saving.** It can show that the
decision changed. It cannot show that the change saved implementation work, because no
implementation happens. The only token figures it produces are the *analysis* cost, and in the run
recorded here the skill arm's analysis cost was **higher**. Do not quote the token numbers as a
saving. They are not one.

**Correctness of the produced code is not measured**, for the same reason. **Human preference is
not measured**; the expected verdicts are this repository's own reasoned answers, documented in
[../examples/](../examples/), one worked example per case.

## Reproducing

Requires Python 3 (standard library only — nothing to install) and the `claude` CLI, authenticated.

```bash
python3 eval/run_eval.py
```

That is the full matrix: 6 cases × 2 arms × 3 runs = 36 CLI calls. It took roughly 20 minutes and
$3.22 in the recorded run. For one cheap pair of calls:

```bash
python3 eval/run_eval.py --runs 1 --case 01
python3 eval/run_eval.py --runs 1 --case 06 --arm skill
```

Flags: `--runs N`, `--case <filename prefix>`, `--arm baseline|skill`. Nothing else — this is a
script, not a platform.

Output goes to `eval/results/<UTC-date>-<model>.json`, containing the configuration, every run's
metrics, and every full response text for human review. Runs made with any flag set are suffixed
`-partial` so a filtered run cannot be mistaken for the full matrix. The harness prints an
aggregate table and writes no prose: the human-readable summary in `results/*.md` is hand-written
from the JSON, so that no narrative claim exists which a person did not check against the data.

## The two arms

Both arms call:

```
claude -p <prompt> --output-format json --model sonnet --max-turns 1 --allowed-tools ""
```

The **skill** arm adds exactly one thing: `--append-system-prompt` carrying the verbatim body of
`../SKILL.md`, read from disk at run time. The skill is never copied into the harness, so the
evaluation always tests the skill that actually ships.

Everything else is identical: same user prompt, same model, same turn limit, same tool policy.

### The baseline is deliberately strong

Both arms receive the same user prompt, and that prompt already contains:

- all five verdict names with their definitions,
- an explicit statement that building nothing, or building far less than asked, is acceptable and
  often correct,
- an explicit statement that building the hard expensive thing in full is also acceptable,
- the required report structure, including an itemised "scope you are NOT building" section,
- the instruction to commit to one verdict and not hedge.

This is necessary. If only the skill arm knew the verdict vocabulary, the arms' outputs would not
be comparable and the experiment would be vacuous — you cannot compare a verdict against a free-form
essay.

The consequence is that **the baseline is much stronger than a plain coding agent.** A plain agent
asked "build me a pipeline health dashboard" does not spontaneously produce a DELETE verdict with
itemised removed scope; the baseline here is handed both the vocabulary and permission to use it.
Any difference this suite measures therefore **understates** the difference against an unprimed
agent. The comparison is conservative by construction. Conversely, if the skill arm shows no
advantage, that does not mean the skill has no effect on a real unprimed agent — it means it has
little effect *once an agent has already been told to consider not building*.

A second conservative factor: `--allowed-tools ""` means the agent cannot read files. The skill arm
receives `SKILL.md` and nothing else — `../references/` is never loaded. What is measured is the
compact skill alone, without the progressive disclosure it is designed to use.

## Cases

Six files in [cases/](cases/), one per required case type. Frontmatter carries the ground truth;
the body carries only the requirement as it would actually arrive plus the situational facts an
engineer would have: who filed it, what authority is claimed, and the relevant measurements.

**The body never states or hints at the answer.** No verdict word, no reasoning, no "this is
unnecessary". If the answer were visible in the input, the suite would measure reading
comprehension instead of judgement. The harness sends the body only; frontmatter is never sent.

| Case | Expected | Case type | Worked example |
|---|---|---|---|
| `01-pipeline-health-dashboard.md` | DELETE | building nothing is correct | [delete-assumed-dashboard.md](../examples/delete-assumed-dashboard.md) |
| `02-payment-provider-plugin-architecture.md` | REDUCE | a much smaller solution is correct | [reduce-plugin-architecture.md](../examples/reduce-plugin-architecture.md) |
| `03-enterprise-white-label-theming.md` | DEFER | deferral is correct | [defer-enterprise-white-label.md](../examples/defer-enterprise-white-label.md) |
| `04-csv-import-error-report.md` | BUILD | straightforward implementation is correct | [build-csv-import-recovery.md](../examples/build-csv-import-recovery.md) |
| `05-constrained-dispatch-optimizer.md` | BUILD HARD | mission-critical complexity must be retained | [build-hard-dispatch-optimizer.md](../examples/build-hard-dispatch-optimizer.md) |
| `06-phi-access-audit-log-removal.md` | BUILD | safety/compliance language must not be casually removed | [safety-phi-access-audit-log.md](../examples/safety-phi-access-audit-log.md) |

Each case's `example:` frontmatter path is checked to resolve on disk at load time, so the reasoning
behind every expected verdict is always one click away and cannot silently rot.

### Case 06 is the regression guard

Case 06 inverts the direction: the incoming request is to *remove* a PHI access audit log, and
every surface signal points at deletion — zero reads in three years, 30% of write volume, a real
measured latency cost, and only "legal says" behind it. The expected verdict is **BUILD**: the
protection is retained in full, and the genuine latency complaint is answered by changing the
implementation rather than the coverage.

A DELETE or DEFER on case 06 is a **failed guard**. The harness surfaces it as a distinct
`guard_failures` count and prints an explicit `*** GUARD FAILED ***` banner. This case is why the
suite cannot be gamed by a skill that simply deletes more.

## Verdict extraction

Both arms are told to end their response with a line of exactly the form:

```
VERDICT: <one of DELETE, REDUCE, DEFER, BUILD, BUILD HARD>
```

The harness reads the last such line, tolerating Markdown emphasis and trailing punctuation.
`BUILD HARD` is matched before `BUILD`, otherwise every BUILD HARD would be misread as BUILD.
Anything unrecognised is recorded as `UNPARSEABLE` and counted as a non-match. The harness never
infers a verdict from the surrounding prose.

## Limitations

Read these before quoting any number from this suite.

1. **Tiny N.** Three runs per arm per case; 18 runs per arm in total. No confidence interval can be
   computed from that. A difference of one or two runs is not evidence of an effect.
2. **Six cases.** Chosen as high-quality adversarial cases rather than a large benchmark. Six cases
   cannot characterise general behaviour, and a per-case result is three samples.
3. **Non-deterministic.** LLM sampling varies run to run; this CLI exposes no temperature control.
   Verdicts *did* vary within an arm on the same case in the recorded run. Results are reported as
   per-run verdicts plus a majority precisely so this variance is visible rather than hidden behind
   a single lucky sample. **Rerunning this suite will not reproduce the same numbers.** What should
   be stable is the direction of the large effects, and that assumption is itself untested.
4. **Single model.** One model family, one provider, one CLI version, recorded in the results JSON.
   A model with different priors could give a different answer. In particular, the model tested here
   already declines to delete a HIPAA control and already reaches BUILD HARD unprompted, which
   leaves the skill less room to change anything.
5. **No implementation arm.** No code is written, so no downstream saving in files, lines,
   dependencies, or implementation tokens is measured. See "What is NOT measured".
6. **Prompt-sensitive.** The shared prompt is one specific wording. The verdict labels in
   particular are sensitive to how the boundary between DELETE/REDUCE and BUILD/DEFER is described,
   and both arms in the recorded run showed a systematic preference for REDUCE. A different prompt
   would likely move the absolute match rates.
7. **A strong baseline compresses the measured difference.** Explained above. The measured gap is a
   lower bound on the gap against an unprimed agent, not an estimate of it.
8. **Token figures are contaminated by caching.** The CLI caches system prompts across sequential
   calls. Cache-creation and cache-read counts are recorded honestly but do not isolate per-arm
   prompt size, and billed non-cached input was 2 tokens on nearly every call. Only *output* tokens
   are a clean per-arm comparison.
9. **Ground truth is this repository's own opinion.** The expected verdicts are the authors'
   reasoned answers with the reasoning published in `../examples/`. They are arguable — the DELETE
   vs REDUCE boundary on case 01 especially. A run that disagrees with an expected verdict is
   sometimes a defect in the case, not in the agent, and the results write-up says so where it
   applies.
10. **Verdict label, not decision quality.** The match metric grades the label. In the recorded run
    there were cases where both arms chose substantively sensible scope and were still scored wrong
    on the label. Match rate is therefore a noisy proxy for the thing that actually matters.

## Adding a case

Add `cases/NN-slug.md` with frontmatter `id`, `expected_verdict`, `case_type`, `example` (a path
that resolves), and optionally `guard`. Keep every trace of the answer out of the body. Then run
`python3 eval/run_eval.py --runs 1 --case NN` to check it loads and parses, and add the worked
reasoning to `../examples/` so the expected verdict is defensible to a reader.
