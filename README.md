# Requirement Zero

**Every requirement must earn its right to exist.**

Before Requirement #1 comes Requirement #0: prove that the requirement deserves to exist.

Requirement Zero is an [Agent Skill](https://code.claude.com/docs/en/skills) that makes an AI
coding agent challenge a requirement *before* it plans or writes code.

## Install

```bash
git clone https://github.com/Chisanan232/requirement-zero.git ~/.claude/skills/requirement-zero
```

That is all of it. The repository root *is* the skill directory — `SKILL.md` is at the top level —
so there is nothing to build, install, or configure afterwards, and updating is `git pull`. The
agent then invokes it on its own when a request matches, or you can ask for it by name.

[USAGE.md](USAGE.md) covers the rest: when it fires and when it must not, how to read each
verdict, how it interacts with your project's existing safety and compliance constraints, known
failure modes, and which hosts this has actually been tested on.

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

## Who it is for

Engineers using AI coding agents on real systems, where the agent is fast enough that
unnecessary scope gets built before anyone stops to question it — and technical leads who would
rather review a challenged requirement than a well-implemented mistake.

## Repository layout

```
SKILL.md      the skill itself, kept deliberately compact
references/   supporting methodology in 4 files, loaded only when needed
examples/     6 worked decisions, one per verdict plus a safety case, and an index
eval/         the evaluation harness, 6 input cases, and published results
USAGE.md      installation, triggers, verdicts, safety boundaries, compatibility
README.md     this file
LICENSE       MIT
```

The skill is a Markdown file: there is no CLI, server, package, or runtime to install.

## Status

v0.1. The skill, its references, the worked examples, the evaluation suite, and the usage
documentation are all in the tree and usable. The verdict set, the ordered discipline, and the
repository layout are settled.

Tested on Claude Code. Not tested on Codex or any other Agent Skills-compatible host — see
[USAGE.md](USAGE.md#compatibility) for exactly what was and was not run, and what verifying
another host would take.

## What v0.1 contains

- `SKILL.md` — the skill, deliberately compact
- `references/` — four supporting documents, loaded only when the agent needs one
- `examples/` — six worked decisions, one per verdict plus a safety case, with an index
- `eval/` — the harness, six adversarial input cases, and one published run
- `USAGE.md` — installation, triggers and non-triggers, verdicts, safety boundaries, failure
  modes, compatibility

What it deliberately does not contain, because none of it is needed to install or run a Markdown
skill:

- No package registry entry, and no package manifest
- No hosted service
- No installer binary or install script
- No MCP server
- No custom runtime, and no dependencies of any kind

Installation is `git clone` into your skills directory. If that ever stops being true, the
project has grown something it did not earn.

## License

[MIT](LICENSE)
