# Using Requirement Zero

Requirement Zero is an [Agent Skill](https://code.claude.com/docs/en/skills): a single
`SKILL.md` file with YAML frontmatter and a Markdown body, plus a `references/` directory the
agent loads only when it needs one. There is no CLI, no server, no package, no runtime, and no
build step.

For what the skill is *for* and where it sits relative to other tools, read
[README.md](README.md). This file is about running it.

## Installation

```bash
git clone https://github.com/Chisanan232/requirement-zero.git ~/.claude/skills/requirement-zero
```

That is the whole installation. There is nothing to build, install, or configure afterwards.

The reason it is one command is that **the repository root is the skill directory**. `SKILL.md`
sits at the top level of the repo, so cloning the repo into a directory under your skills
directory produces exactly the layout a skill is expected to have:

```
~/.claude/skills/requirement-zero/SKILL.md      <- the skill
~/.claude/skills/requirement-zero/references/   <- loaded on demand by the agent
```

Claude Code discovers personal skills from `~/.claude/skills/`, one directory per skill, each
containing a `SKILL.md`. Because the install is a clone, updating is a pull:

```bash
git -C ~/.claude/skills/requirement-zero pull
```

Removing it is deleting that directory. Nothing else on your system was touched.

### Project-scoped install

Claude Code also supports project-scoped skills in `.claude/skills/` inside a repository, which
is the right choice when you want the skill committed alongside a codebase so everyone working
in it gets the same behaviour. The same clone applies, with the destination changed to
`.claude/skills/requirement-zero` in the project.

Verified honestly: the tests behind this document were run against the **personal** location
(`~/.claude/skills/`). The project-scoped location is a documented Claude Code feature, but this
project has not run its own test against it. If you use it, confirm discovery yourself with the
check below before relying on it.

### Confirming it installed

Ask the agent to list the skills available to it. `requirement-zero` should appear. That check
is the one used to verify the install path in this document.

Two things that do **not** work, both established by testing:

- Skills are not discovered via `--plugin-dir`. That flag is for plugins, not skills.
- Skills are not discovered via a relocated `CLAUDE_CONFIG_DIR`.

`~/.claude/skills/` is the path that works.

## Invoking it

There are two paths, and the first is the normal one.

**Automatic.** The agent reads the `description` field in the skill's frontmatter and invokes
the skill when an incoming request matches it. You do not have to name it. Ask for a feature and
the skill fires on its own if the request looks like unvalidated scope.

**Explicit.** Name it in the request when you want it regardless:

> Run requirement-zero on this: we want to add a plugin system to the log parser.

Explicit invocation is useful for a request that sits near the boundary — where the skill might
not have fired by itself, but you want the requirement challenged before any planning happens.
It is also how you get a verdict on a *plan* or a ticket breakdown rather than on a single
feature request.

## When it fires

The frontmatter `description` is the trigger surface. It fires when a request asks to build,
add, or design something **and** the necessity or scope of that thing has not been established.
Named categories:

- New features and capabilities
- Abstractions, interfaces, and plugin systems
- Dashboards and reporting surfaces
- Configurability — settings, flags, options
- Migrations
- Anything phrased as "we should probably support X"

A tested example. Given:

> We should add a plugin system to our log parser so other teams can add their own formats
> later.

the skill fired without being named and returned **DEFER**, on the grounds that "no evidence
found — no team is named, no format is currently blocked, no incident or support request is
cited. The justification is entirely anticipatory." It cited the rule from `SKILL.md` that a
plugin point needs a *committed* second consumer — a named consumer with a date — not an
anticipated one.

That is the shape of request it exists for: a real-sounding requirement whose entire support is
a prediction.

## When NOT to invoke it

This matters as much as the triggers. A skill that fires on everything is worse than no skill:
it adds cost and latency to work that was already decided, and it teaches you to ignore its
output. The `description` excludes three classes explicitly, and
[references/workflow.md](references/workflow.md) adds the stopping rules.

**Already-validated work.** A requirement that has already been challenged and decided, or one
that arrives with its evidence attached. Re-litigating a settled decision is its own waste. The
same applies to mechanical changes with a stated outcome — renames, version bumps, formatting.

**Plain bug fixes.** Restoring intended behaviour is not new scope. Tested: asked about a date
parser with an off-by-one error on December, the agent replied that requirement-zero does not
apply — "this is a concrete bug fix with a clear, observable incorrect behavior. Bug fixes are
explicitly excluded from its scope." The ambiguous case is a large bug fix that implies new
architecture: fix the bug, and run the discipline on the proposed architecture separately.

**Explicit safety, security, legal, or compliance requirements.** Tested: given "a pen test
found our login endpoint has no rate limit and we are seeing credential stuffing in
production", the agent replied that requirement-zero does not apply — "credential stuffing is
already happening in production, making this a confirmed incident response, not a speculative
feature. Requirement-zero is explicitly excluded for safety, security, legal, or compliance
requirements."

Both of those non-trigger answers came from the `description` frontmatter alone, without the
skill body being loaded. The exclusion is part of the trigger surface, not a rule buried inside
the method.

**Trivial requests.** Nothing in the skill stops you asking for a verdict on a one-line change,
but the analysis costs tokens and time (see [Cost](#cost)) and produces nothing you did not
already know.

## Reading a verdict

Every run ends in exactly one of five verdicts. The skill is required to commit — it must not
present the five as options for you to pick from, and it must not hedge into "it depends".

Whatever the verdict, the run owes you the same six-part report: the fundamental objective, the
evidence and its provenance, the verdict, the **deleted scope** itemized, the **retained scope**
itemized, and one concrete next action. The two scope lists are the reviewable part. "Simplified
the design" is not a reviewable output; "removed the plugin registry, the YAML config, and the
two unused adapters" is.

### DELETE — build nothing

No observer and no signal could be named for the requirement as a whole, or the system already
does this.

*What you owe it:* a decision. Either accept it and close the request, or supply the missing
piece — who is affected, or what breaks without it. Do not argue with it by restating the
request; that changes nothing and the skill will say so.

### REDUCE — the need is real, the proposed scope is not

The core outcome survived, but named parts did not. This is the most common correct answer for a
real request.

*What you owe it:* read the deleted-scope list, item by item, and object to any item you
disagree with. That list is the whole product of a REDUCE verdict. If you accept it, hold the
implementation to it — deleted scope most often returns during implementation as "easy while I'm
here".

### DEFER — plausible, but nothing is blocked today

Value is real or plausible but the only support is a prediction, or the value is genuinely
adjacent to the core. A DEFER verdict must name the **concrete trigger** that would revive it.

*What you owe it:* check that the trigger is something that will actually be noticed when it
happens — a customer signing, a second format arriving, a measured number crossing a threshold.
A trigger nobody will observe is a DELETE wearing a nicer label. Then park the request against
that trigger rather than leaving it in a backlog to rot.

### BUILD — necessary, and build the smallest sufficient version

Evidence supports the outcome and it is core to what the system is for.

*What you owe it:* build the retained scope and nothing beyond it. If implementation reveals the
retained scope is insufficient, stop and re-state the verdict with the new information rather
than silently expanding.

### BUILD HARD — the difficulty is the mission, do not simplify it away

Core, and the cheap version provably fails the outcome. This verdict exists because a method
that can only shrink things is a bias, not a discipline — minimalism is not the objective.

*What you owe it:* **check its homework.** A BUILD HARD verdict is invalid unless it names both
(a) the simpler version it considered and (b) the specific way that simpler version fails the
outcome. If either is missing, it must be downgraded to BUILD and re-sized. That check is the
only thing preventing BUILD HARD from becoming a rubber stamp for expensive work, so make it
every time.

For a worked decision in each direction, see [examples/index.md](examples/index.md) — six full
cases, one per verdict plus a safety case.
