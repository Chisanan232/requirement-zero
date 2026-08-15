# Requirement Zero

**Every requirement must earn its right to exist.**

Before Requirement #1 comes Requirement #0: prove that the requirement deserves to exist.

Requirement Zero is an [Agent Skill](https://code.claude.com/docs/en/skills) that makes an AI
coding agent challenge a requirement *before* it plans or writes code.

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

## Who it is for

Engineers using AI coding agents on real systems, where the agent is fast enough that
unnecessary scope gets built before anyone stops to question it — and technical leads who would
rather review a challenged requirement than a well-implemented mistake.

## Repository layout

```
SKILL.md      the skill itself, kept deliberately compact
references/   supporting methodology, loaded only when needed  (planned)
```

Installation and usage documentation land with v0.1. The skill is a Markdown file: there is no
CLI, server, package, or runtime to install.

## Status

Pre-v0.1, under active development. The verdict set and layout above are settled; content is
still landing.

## License

[MIT](LICENSE)
