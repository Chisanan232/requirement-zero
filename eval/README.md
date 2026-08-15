# Evaluation suite

Requirement Zero is a Markdown skill that makes a coding agent decide whether a requirement
deserves to exist before it designs or builds anything. It commits to one of five verdicts:
**DELETE**, **REDUCE**, **DEFER**, **BUILD**, **BUILD HARD**. See [../SKILL.md](../SKILL.md).

The harness serves two skills, selected with `--profile`. This file documents the Requirement Zero
profile, which is the default, and the design decisions that apply to both — the two arms, the
isolation flags, verdict extraction, why the baseline is deliberately strong, and why the token
figures are not a saving. The Codebase Zero profile has its own corpus, its own guards, and its own
results: [codebase-zero/README.md](codebase-zero/README.md).

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
| **Guard failures** | False rejections on any case carrying a `guard:` frontmatter key. The key's value names what that case guards and is per corpus — this profile's is `safety-constraint-not-deleted`; the codebase-zero corpus uses three others. Any non-zero value here means the suite caught over-aggressive deletion, and is reported loudly by the harness. |
| **Unparseable** | Runs where the model answered but produced no readable `VERDICT:` line. Counted as non-matches. Never guessed at. |
| **Errored** | Runs where the CLI itself failed (`is_error`, or empty result — e.g. the turn was consumed by an attempted tool call). Reported separately and **excluded from match-rate denominators**, because a harness failure is not a wrong answer. Non-zero means the run needs investigating before any number is quoted. |
| Output / input / cache-creation / cache-read tokens, cost, duration | Taken verbatim from the CLI's JSON `usage` and `total_cost_usd`. |
| Model string | Taken from the CLI's `modelUsage` key, so the recorded model is the one actually served, not the one requested. |
| Named its non-built scope | Floor check only: did the response state what it is *not* building. Both arms are asked for that section, so it sits at ceiling in both. It is **non-discriminating by construction** and must not be read as an arm difference — see the disclosure in the results file. |

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

Flags: `--profile requirement-zero|codebase-zero`, `--runs N`, `--case <filename prefix>`,
`--arm baseline|skill`, and `--self-test` (checks verdict parsing against known-tricky strings for
both profiles, and checks each skill's `description` is present, within the host's listing cap, and
still names its load-bearing terms; makes no API calls and costs nothing). Nothing else — this is a
script, not a platform.

Each profile carries its own skill path, case directory, prompt, verdict vocabulary, and definition
of a false rejection, so adding the second skill did not require a second copy of the harness. Three
things a profile cannot get wrong quietly: guard cases are selected by their `guard:` frontmatter key
rather than by filename, so a corpus that numbers its cases differently cannot silently lose its
guards; a case that declares `guard:` while expecting a scope-losing verdict is rejected at load
time, because such a guard would inflate the guard run count while being structurally unable to fail;
and each profile's `protective_verdicts` and `false_rejections` are checked at import to be non-empty,
to name verdicts the profile can actually return, and not to overlap. That last check exists because
an empty or typo'd `false_rejections` scores zero on every run, which is exactly the published value
and therefore indistinguishable from the correct answer.

The harness resolves all paths relative to its own location, so it behaves identically from any
working directory.

Output goes to `eval/results/<UTC-date>-<model>.json`, containing the configuration, every run's
metrics, and every full response text for human review. Runs made with any flag set are suffixed
`-partial` so a filtered run cannot be mistaken for the full matrix. The harness prints an
aggregate table and writes no prose: the human-readable summary in `results/*.md` is hand-written
from the JSON, so that no narrative claim exists which a person did not check against the data.

## The two arms

Both arms call:

```
claude -p <prompt> --output-format json --model sonnet --max-turns 1 --tools "" --safe-mode
```

The **skill** arm adds exactly one thing: `--append-system-prompt` carrying the verbatim body of
`../SKILL.md`, read from disk at run time. The skill is never copied into the harness, so the
evaluation always tests the skill that actually ships. Each results file records a SHA-256 of the
exact skill body used, so the version under test is machine-verifiable rather than pinned by a
hand-typed commit reference. If `SKILL.md` ever loses its body, the harness aborts rather than
running two silently identical arms.

`--tools ""` and `--safe-mode` are load-bearing for validity, not incidental — see
[Isolation](#isolation).

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

A second conservative factor: `--tools ""` means the agent has no tools, so it cannot read files.
The skill arm receives `SKILL.md` and nothing else — `../references/` is never loaded. What is
measured is the compact skill alone, without the progressive disclosure it is designed to use.

## Isolation

Two flags exist purely to make the comparison valid. Both were added after an earlier run was found
to be contaminated, and both are worth understanding before trusting any number here.

### `--safe-mode` — no ambient project instructions

Claude Code discovers `CLAUDE.md` files from the working directory upward and prepends them to the
system prompt. That is useful in normal work and fatal here: **whatever engineering guidance happens
to sit above the checkout gets injected into both arms.** If that guidance says anything about
scope, minimalism, or not adding unrequested abstractions — which such files very often do — then
the "baseline" is not a baseline at all. It is an agent already carrying a partial, uncontrolled
paraphrase of the skill under test, and the measured effect of the skill shrinks toward zero for a
reason that has nothing to do with the skill.

This was not hypothetical. In this repository's environment an ambient file 40,000 characters long
sat two directories above the checkout, and a probe under the old flags returned the sentence
*"Propose the smallest change that achieves the goal"* verbatim when the agent was asked whether its
instructions covered proposing minimal changes. Measured input per call fell from roughly 35,000
tokens to about 3,400 once `--safe-mode` was added, and cost per call fell from about $0.10 to about
$0.03.

`--safe-mode` suppresses that discovery, which has a second benefit: **the run stops depending on
the machine it runs on.** Without it, the same command in the same repo produces different prompts
for different users, and "reproducible" is not a claim anyone can make. `--append-system-prompt`
still works under `--safe-mode`, so the skill arm is unaffected — verified with a sentinel probe
before adopting it.

Residual, stated plainly: `--safe-mode` removes *project* instruction files, not the CLI's own
built-in system prompt. Probed directly, that built-in prompt still contains generic
minimal-change guidance of its own. So the baseline is *still* not a naive agent, and this remains a
conservative comparison — it is simply no longer contaminated by an uncontrolled, machine-specific
file. This residual applies equally to both arms and cannot be removed through this CLI.

### `--tools ""` — tools actually removed

`--allowed-tools ""` does **not** disable tools. It is a permission allow-list: the tools stay in
the model's schema, and an attempted call is denied, which consumes the single allowed turn and
returns `is_error: true` with no result text. `--tools ""` removes the tools from the schema
outright. Verified both ways with a probe that asks the agent to read a file: under
`--allowed-tools ""` the run failed with `error_max_turns` and an empty result; under `--tools ""`
the run succeeded in one turn.

This matters twice over. It is what actually substantiates the claim above that `../references/`
can never be loaded, and it removes a silent-failure path: a failed run returns no text, which
would parse as a missing verdict and be scored as a *wrong answer* rather than as an error. The
harness now records such runs as `ERRORED`, excludes them from match-rate denominators, and prints
a warning banner. Any results file reporting a non-zero `errored_runs` should be treated as suspect
until the cause is understood.

## Cases

Six files in [cases/](cases/), one per required case type. Frontmatter carries the ground truth;
the body carries only the requirement as it would actually arrive plus the situational facts an
engineer would have: who filed it, what authority is claimed, and the relevant measurements.

**The body never states or hints at the answer.** No verdict word, no reasoning, no "this is
unnecessary". If the answer were visible in the input, the suite would measure reading
comprehension instead of judgement. The harness sends the body only; frontmatter is never sent.

Checking for leaked *verdict words* is not sufficient, and an earlier version of case 06 failed on
exactly that point: it stated the governing regulation, the contract, and the confirming officer as
given facts, so the correct answer could be reached by restating the input and the guard could not
fail. Reasoning leaks are the harder class. When adding or editing a case, grep for citations,
statute numbers, authority confirmations, and any sentence that supplies the decisive argument
rather than the raw situation.

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

Case 06 inverts the direction: the incoming request is to *remove* a patient-record access log, and
every surface signal points at deletion — zero reads in three years, 30% of write volume, a real
measured latency cost, and only "legal says" behind it, with nobody able to name a rule.

Crucially, the case body **withholds the justification**. It does not name a regulation, quote a
contract, or report a compliance officer's confirmation, and it does not supply the argument that
defeats the 10%-sampling alternative. It gives only what the filing engineer actually knows: the
costs, the absence of reads, the vague authority, the domain (patient records for hospital
customers), and the fact that nobody outside his own colleagues has been asked.

That makes it a real test of the asymmetry doctrine rather than a reading exercise. The doctrine —
stated in `../SKILL.md` and expanded in `../references/provenance.md` — is that for a *protective*
constraint, absent provenance triggers research and escalation while the protection is retained; it
does not license removal. An arm that reaches the right answer here must apply that asymmetry to a
requirement whose justification it cannot see.

The expected verdict is **BUILD**: coverage is retained in full, and the genuine latency complaint
is answered by changing the implementation. A DELETE or DEFER is a **failed guard**; so, in
substance, is accepting the 10% sampling offer, since that is coverage reduction in a performance
costume. The harness surfaces guard failures as a distinct `guard_failures` count and prints an
explicit `*** GUARD FAILED ***` banner. This case is why the suite cannot be gamed by a skill that
simply deletes more — and because the answer is no longer in the input, it is a case either arm can
genuinely fail.

## Verdict extraction

Both arms are told to end their response with a line of exactly the form:

```
VERDICT: <one of DELETE, REDUCE, DEFER, BUILD, BUILD HARD>
```

The harness reads the last such line. `BUILD HARD` is matched before `BUILD`, otherwise every
BUILD HARD would be misread as BUILD. Anything unrecognised is recorded as `UNPARSEABLE` and counted
as a non-match. The harness never infers a verdict from the surrounding prose.

Matching on longest-first alone is not enough, because models decorate the verdict in ways that
break naive prefix comparison: `BUILD **HARD**`, `` `BUILD HARD` ``, `BUILD-HARD`, a non-breaking
space, a leading `>` quote marker, doubled spaces. Every one of those silently produced `BUILD`
or `UNPARSEABLE` in an earlier version. The parser now strips emphasis, backticks, quote markers,
and hyphens, normalises whitespace including non-breaking spaces, and only then matches.

Because this one function decides every other number in the suite, it has its own test:

```bash
python3 eval/run_eval.py --self-test
```

That checks 32 known-tricky strings, **each against the real vocabulary of the profile it belongs
to** — the same tuple a paid run uses. That detail is the point of the test rather than an
implementation note: an earlier version ran every case against the union of both profiles'
verdicts, which is ordered correctly by construction, so the test passed even with a mis-ordered
profile tuple and could not detect the one failure it exists to catch. The cases now include the
cross-profile negatives (`DEFER` alone is not a codebase-zero verdict; `CONSOLIDATE` is not a
requirement-zero one), which must come back `UNPARSEABLE` rather than being guessed at.

The ordering invariant itself is enforced separately, at import: `_assert_prefix_safe` refuses to
start if any profile lists a verdict before one it is a prefix of, so `DEFER` ahead of
`DEFER CLEANUP` is a startup failure, not a silently corrupted run.

Both make no API calls and cost nothing. Run the self-test after touching the parser, and after
editing either skill's `description` — the description is the trigger surface, so a category dropped
from it cannot be recovered by anything in the skill body, and `--self-test` is what notices.

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
   A model with different priors could give a different answer. The model tested here already
   reaches BUILD HARD unprompted on the hardest case, which leaves the skill less room to change
   anything.
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
11. **Ambient instruction contamination — now controlled, previously not.** Claude Code injects any
    `CLAUDE.md` found from the working directory upward. An earlier run of this suite was invalidated
    by exactly that: a large ambient engineering-guidance file was silently added to *both* arms, and
    it contained scope-discipline language paraphrasing part of the skill under test, which
    strengthened the baseline for reasons unrelated to the experiment. `--safe-mode` now suppresses
    it, and the results file records the isolation flags used. Any results file without
    `isolation_flags` predates the fix and should not be trusted. A residual remains: the CLI's own
    built-in system prompt still contains generic minimal-change guidance that cannot be removed
    through this interface, so the baseline is not a naive agent. See [Isolation](#isolation).
12. **`--tools ""` is required to disable tools; `--allowed-tools ""` does not.** Any results file
    produced with the latter carries an unverified no-file-reads claim and a silent failure path
    where a CLI error is scored as a wrong answer. See [Isolation](#isolation).

## Adding a case

Add `cases/NN-slug.md` with frontmatter `id`, `expected_verdict`, `case_type`, `example` (a path
that resolves), and optionally `guard`. Keep every trace of the answer out of the body — including
the *reasoning*, not just the verdict word. Then run `python3 eval/run_eval.py --runs 1 --case NN`
to check it loads and parses, and add the worked reasoning to `../examples/` so the expected verdict
is defensible to a reader.
