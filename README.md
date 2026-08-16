# Requirement Zero

**Every requirement must earn its right to exist.**

Before Requirement #1 comes Requirement #0: prove that the requirement deserves to exist.

Requirement Zero is an [Agent Skill](https://code.claude.com/docs/en/skills) that makes an AI
coding agent challenge a requirement *before* it plans or writes code.

This repository holds two skills. **Requirement Zero** challenges a requirement before it is built.
**[Codebase Zero](skills/codebase-zero/SKILL.md)** audits an artifact that already exists and asks
whether it still deserves to exist — see [that section](#codebase-zero) below.

## Install

```bash
git clone https://github.com/Chisanan232/requirement-zero.git ~/.claude/skills/requirement-zero
ln -s ~/.claude/skills/requirement-zero/skills/codebase-zero ~/.claude/skills/codebase-zero
```

The first line installs Requirement Zero: the repository root *is* the skill directory — `SKILL.md`
is at the top level — so there is nothing to build or configure, and updating is `git pull`. The
second line installs Codebase Zero under its own bare name, and it is needed because a skill nested
inside another skill's directory is **not** discovered by the skills-directory scan — tested, not
assumed. The symlink points into the clone, so `git pull` still updates both. (If you skip the
second line, the clone is still loaded as a plugin and Codebase Zero reaches the agent as
`requirement-zero:codebase-zero` instead — a different name, which is why the symlink is the
documented route; [USAGE.md](USAGE.md#claude-code-plugin-marketplace) compares them.)

The agent then invokes either skill on its own when a request matches, or you can ask for one by
name.

Or install both with the [`skills` CLI](https://github.com/vercel-labs/skills), which flattens the
pair into siblings so no symlink is needed for this Claude-Code-only target:

```bash
npx skills@1.5.22 add Chisanan232/requirement-zero --full-depth --skill '*' --agent claude-code -y
```

`--full-depth` is what gets Codebase Zero installed under its own bare name: without it the CLI
finds only Requirement Zero, because the root `SKILL.md` shadows the nested one. (At the personal
location, Codebase Zero still reaches the agent either way, as `requirement-zero:codebase-zero`,
because the copied tree includes `.claude-plugin/`. At the project location below, that only
happens once you have trusted the workspace.) That command installs into the **current directory**
(`./.claude/skills/`) and writes a `skills-lock.json` beside it, not into `~/.claude/skills/` —
add `-g` for the personal location used above. Verified on CLI 1.5.22 with Claude Code 2.1.226 —
see [USAGE.md](USAGE.md#installing-with-the-skills-cli) for what was and was not tested.

[USAGE.md](USAGE.md) covers the rest: both install paths and what was actually tested, when each
skill fires and when it must not, how to read each verdict, how they interact with your project's
existing safety and compliance constraints, known failure modes, and which hosts this has actually
been tested on. Most of its observed behaviour — the trigger and non-trigger runs, the failure
modes, the cost figures — is Requirement Zero's; it says so where Codebase Zero has no equivalent
evidence yet.

## The problem

Coding agents are very good at satisfying a stated request. That is exactly the failure mode.
Given "add a plugin architecture", a capable agent will design it, implement it, test it,
document it, and polish it — efficiently producing work that should never have existed.

The cost of this addition bias is not bad code. It is *good code that solves a requirement
nobody validated*: the abstraction with one implementation, the dashboard nobody opens, the
configurability for a second provider that never arrives.

An agent that only asks "how do I build this well?" cannot catch that. Something has to ask
"should this exist at all?" first.

## What it does

For a non-trivial request, Requirement Zero traces the requirement back to the fundamental
objective and the evidence behind it, then commits to one of five verdicts:

| Verdict | Meaning |
|---|---|
| **DELETE** | The requirement does not earn its existence. Build nothing. |
| **REDUCE** | The need is real; the proposed scope is larger than the need. |
| **DEFER** | Plausible value, insufficient present evidence. Revisit on a trigger. |
| **BUILD** | Necessary and aligned to the objective. Build the smallest sufficient version. |
| **BUILD HARD** | Expensive and difficult, but it *is* the mission-critical bottleneck. Do not simplify it away. |

The discipline is ordered, and the order is the point:

**question → delete → focus → simplify → accelerate → automate**

Deleting is attempted before simplifying, because simplifying something unnecessary is wasted
work. Automating comes last, because automating an unproven workflow just makes an unnecessary
process cheaper to keep.

## Worked examples

[**examples/index.md**](examples/index.md) has six full decisions, one per verdict plus a safety
case, each showing the requirement as it arrived, the evidence, the verdict, and the itemized
deleted and retained scope. If you read two, read
[the DELETE case](examples/delete-assumed-dashboard.md) and
[the BUILD HARD case](examples/build-hard-dispatch-optimizer.md) — they are the two ends of the
range.

## What it is not

**Not a persona or a celebrity chatbot.** The methodology is inspired by subtraction-first,
first-principles operating practice, but this project imitates no one's personality, voice, or
opinions. It encodes the repeatable engineering parts and nothing else. You do not need to know
anything about the history of the method to use it.

**Not a code minimizer, and not YAGNI-in-a-prompt.** Tools that shrink implementations, audit
dead code, or flag over-engineering operate on code that has already been decided on.
Requirement Zero operates one step earlier, on the requirement itself — and it reaches a
different kind of conclusion: *don't build this*, or *the real job here is much smaller than
what you asked for*.

**Minimalism is not the objective.** This is the distinction that most "keep it simple" prompts
get wrong. Some work is genuinely hard and must stay hard, because the difficulty is where the
mission actually lives. Requirement Zero has to be as willing to say **BUILD HARD** as to say
**DELETE**, or it is just an excuse to under-build.

**Not a deletion license for safety work.** Security, legal, privacy, safety, and compatibility
constraints are not deleted for lack of a convenient justification. Absent evidence lowers
confidence in *speculative* scope; it does not license removing a protection. Those constraints
require concrete evidence and appropriate review before anything is dropped.

## Evaluation

Requirement Zero's published run is below; Codebase Zero's is
[**further down**](#codebase-zero-evaluation).

There is one published run: 36 CLI calls, `claude-sonnet-4-6`, six adversarial cases, two arms
(baseline and skill-enabled), three runs per cell. Full write-up in
[**eval/results/2026-08-15-claude-sonnet-4-6.md**](eval/results/2026-08-15-claude-sonnet-4-6.md);
design, metrics, and limitations in [**eval/README.md**](eval/README.md).

The honest reading, both halves of which have to be quoted together:

- **No detectable difference in verdict accuracy.** The skill arm matched the expected verdict on
  one more run out of 18 than the baseline. At three runs per cell that is a single run of
  difference and no confidence interval can be computed from it; a rerun could reverse the
  ordering.
- **The skill arm cost more.** Output tokens rose from 25,899 to 31,464 across 18 calls and mean
  latency rose from 30.2 s to 36.4 s. There is no implementation arm, so the downstream saving the
  method claims is **entirely unmeasured** — only the analysis cost was measured, and it went up.

Two results are worth naming. Both arms produced **zero false rejections**: no run refused valid
work or under-built a requirement that should have been built, and the only over-deletion anywhere
in the matrix came from the *baseline*. The clearest behavioural difference is case 03, where the
skill arm reached DEFER on 2 of 3 runs against the baseline's 0 of 3 — a genuine
build-nothing-yet decision on speculative scope, on one case out of six. It is offset by case 06,
where the skill arm's *label* went the other way (REDUCE 3/3 against the baseline's BUILD 2/3)
while the protective behaviour was identical in both arms. The aggregate is a near-cancellation of
movements in both directions, not a lift.

Reproducing it needs Python 3 and the `claude` CLI and nothing else: `python3 eval/run_eval.py`.

## Codebase Zero

Requirement Zero acts before anything is built. **[Codebase Zero](skills/codebase-zero/SKILL.md)**
is the sibling skill for the stage after: a codebase that has accumulated abstractions, compatibility
layers, dependencies, flags, configuration, and operational machinery, where the question is no
longer *should we build this* but **does this still deserve to exist?**

It audits an artifact against the system's mission, gathers evidence from references, tests,
configuration, and git history, and commits to one of six verdicts:

| Verdict | Meaning |
|---|---|
| **DELETE** | No current dependent, no observer of its absence, original requirement gone. |
| **CONSOLIDATE** | Several artifacts do one job; the behaviour stays and one survives. |
| **SIMPLIFY** | The behaviour is justified; the structure around it is not. |
| **DEFER CLEANUP** | Looks removable, but the evidence or the risk does not justify acting now. |
| **KEEP** | It still earns its place. |
| **INVEST** | Expensive and complex, *and* where the mission is won or lost. Spend more here. |

It **audits by default** and does not delete code on its own authority. Every non-trivial verdict
carries seven fields — objective, evidence, confidence, blast radius, benefit and cost, what is
retained, and the verification that would catch a mistake.

The reason it is not a dead-code detector: the three cases it is built around are ones where every
in-repository signal points at deletion and deletion would be expensive — a three-year-untouched file
that is still a live customer contract, a payment guard whose counter has not fired in fourteen
months, and the highest-churn subsystem in the repository, which is where the next quarter should go.
A static analyzer is better than this at finding unreferenced symbols and should be run first;
[skills/codebase-zero/DIFFERENTIATION.md](skills/codebase-zero/DIFFERENTIATION.md) states that
overlap plainly, including when to use the other tool instead.

Seven worked audits: [skills/codebase-zero/examples/index.md](skills/codebase-zero/examples/index.md).

### Codebase Zero evaluation

One published run: 42 CLI calls, `claude-sonnet-4-6`, seven cases, two arms, three runs per cell.
Full write-up in
[**eval/codebase-zero/results/2026-08-15-claude-sonnet-4-6.md**](eval/codebase-zero/results/2026-08-15-claude-sonnet-4-6.md);
design and limitations in [**eval/codebase-zero/README.md**](eval/codebase-zero/README.md).

The skill arm matched the expected verdict on **21/21** runs against the baseline's **17/21** — a
wider and more consistent gap than the Requirement Zero suite produced. Both halves of the reading
have to be quoted together:

- **All four baseline misses kept the artifact anyway.** Every one is on a KEEP case, and in every
  one the baseline chose an adjacent label — DEFER CLEANUP or INVEST — while still concluding the
  thing stays. Across all 42 runs, **neither arm ever recommended removing or reducing a
  load-bearing artifact**: zero false rejections, zero guard failures on all three guard cases. The
  gap is label conformance, not a measured reduction in dangerous behaviour, because no dangerous
  behaviour occurred in either arm.
- **On the four removal cases the arms are identical, 12/12 each.** DELETE, CONSOLIDATE, SIMPLIFY and
  the deliberately hardest case — the orphaned module that only an out-of-repository config value
  saves — were 3/3 in both arms with no disagreement on any run. This suite measured **no difference
  at all** in removal decisions.
- **The skill arm cost more:** output tokens 26,071 → 30,597 (+17.4%), mean latency 26.9 s → 31.5 s.
  There is no arm that acts on the audit, so the engineering time a correct decision saves is
  **entirely unmeasured**.

The one real doctrinal difference is on the payment guard whose duplicate counter has not fired in
fourteen months: the baseline left removal open pending outside evidence, while the skill arm closed
it from the evidence present — a quiet guard is what a working guard looks like — in 3/3 runs. The
larger caveat is that the baseline is strong: this model already answers INVEST on the matching engine
unprompted, so there was little headroom for the skill to show an effect. A weaker model would
discriminate better, and this run says nothing about one.

Reproducing it: `python3 eval/run_eval.py --profile codebase-zero`.

## Who it is for

Engineers using AI coding agents on real systems, where the agent is fast enough that
unnecessary scope gets built before anyone stops to question it — and technical leads who would
rather review a challenged requirement than a well-implemented mistake.

## Repository layout

```
SKILL.md                  Requirement Zero, kept deliberately compact
references/               supporting methodology in 4 files, loaded only when needed
examples/                 6 worked decisions, one per verdict plus a safety case, and an index
skills/codebase-zero/     Codebase Zero: SKILL.md, 3 references, 7 worked audits,
                          and DIFFERENTIATION.md
eval/                     the shared harness, Requirement Zero's 6 cases, published results
eval/codebase-zero/       Codebase Zero's 7 cases and published results
USAGE.md                  installation, triggers, verdicts, safety boundaries, compatibility
README.md                 this file
LICENSE                   MIT
```

Both skills are Markdown files: there is no CLI, server, package, or runtime to install. One
evaluation harness serves both, selected with `--profile`, rather than a second copy of the same
script.

## Status

v0.2. Requirement Zero is unchanged and settled: verdict set, ordered discipline, references,
examples, evaluation. Codebase Zero is new in this version — the skill, three references, seven
worked audits, a differentiation document, and a seven-case evaluation are all in the tree and
usable.

Tested on Claude Code 2.1.226. Not tested on Codex or any other Agent Skills-compatible host — see
[USAGE.md](USAGE.md#compatibility) for exactly what was and was not run, and what verifying
another host would take.

## What is in the tree

- `SKILL.md` — Requirement Zero, deliberately compact
- `references/` — four supporting documents, loaded only when the agent needs one
- `examples/` — six worked decisions, one per verdict plus a safety case, with an index
- `skills/codebase-zero/` — Codebase Zero: the skill, three references, seven worked audits, and a
  document stating where it overlaps with existing tools and when to use those instead
- `eval/` — one harness with two profiles, thirteen adversarial cases in total, and published runs
- `.claude-plugin/` — two small manifests that let Claude Code install this repository as a plugin,
  pointing at the skill files above rather than copying them
- `USAGE.md` — installation for both skills, triggers and non-triggers, verdicts, safety boundaries,
  failure modes, compatibility

What it deliberately does not contain, because none of it is needed to install or run a Markdown
skill:

- No package registry entry, and no package manifest
- No hosted service
- No installer binary or install script
- No MCP server
- No custom runtime, and no dependencies of any kind

The project's own installation is `git clone` into your skills directory. If that ever stops
being true, the project has grown something it did not earn. (The third-party `skills` CLI above
is a different thing: it installs this repository as-is, and the repository ships nothing to
support it.)

## License

[MIT](LICENSE)
