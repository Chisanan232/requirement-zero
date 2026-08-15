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

Claude Code also documents project-scoped skills in `.claude/skills/` inside a repository, which
is the usual choice when you want the skill committed alongside a codebase so everyone working in
it gets the same behaviour. This project did not test that location: every result in this document
was produced against the **personal** location (`~/.claude/skills/`). Treat it as untested and
confirm discovery yourself with the check below before relying on it.

One thing to get right if you do. A plain `git clone` into `.claude/skills/requirement-zero`
leaves a nested git repository, which your project records as a gitlink rather than as committed
files — so it will *not* travel with clones of your project, which is usually the whole reason for
choosing this location. Two ways to actually get it there.

Copy the files in without their `.git` directory. They become ordinary committed files, so every
plain clone of your project has the skill on disk. The trade is that updating is no longer
`git pull` — you recopy.

Or add it as a submodule:

```bash
git submodule add https://github.com/Chisanan232/requirement-zero.git .claude/skills/requirement-zero
```

That keeps `git pull` updates, but a submodule commits a pointer rather than the files, so a
colleague running a plain `git clone` of your project still gets an empty directory. They need
`git clone --recurse-submodules`, or `git submodule update --init` afterwards, before the skill
is on disk at all.

### Confirming it installed

Ask the agent to list the skills available to it. `requirement-zero` should appear. That check
is the one used to verify the install path in this document.

Two things that do **not** work, both established by testing:

- Skills are not discovered via `--plugin-dir`.
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

Both of those refusals cited the exclusion that the `description` frontmatter states verbatim. The
exclusion is part of the trigger surface, not a rule buried inside the method. What was observed is
the refusal and its stated reasoning; whether the host had loaded the skill body is not something
this project could see.

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

## Interaction with your existing project instructions

Read this section before installing the skill into a project where safety, security, privacy,
legal, compliance, or published-interface obligations exist. It is the most important section in
this file.

**Requirement Zero does not override those constraints.** If your `CLAUDE.md`, your architecture
rules, your security policy, or a regulation requires something, this skill is not a mechanism
for arguing it away. Its scope is *unvalidated new scope*, and protective constraints are not
that.

### The asymmetry that makes this coherent

It would be incoherent to demand evidence for everything and then exempt some things by fiat.
The rule is not an exemption; it is that missing evidence means two different things depending
on what is missing evidence.

| Requirement type | Examples | Effect of absent evidence |
|---|---|---|
| **Speculative** scope | future flexibility, anticipated scale, unrequested generality, a plugin point for a consumer who does not exist | Lowers confidence. Pushes toward DELETE or DEFER. |
| **Protective** constraints | security, safety, privacy, data integrity, legal and regulatory obligations, backward compatibility of a published interface | Does **not** license removal. The default is **retain**. |

For a protective constraint, removal requires a named owner's decision and, where applicable,
security, legal, or compliance review, with the residual risk recorded in writing. "Nobody could
name the rule" is a trigger to go and find out who owns it — not a finding that the protection is
unnecessary. Absence of evidence about a threat is not evidence that the protection is
unneeded, and that inference is backwards precisely where it is most expensive.

### What the skill may legitimately do to a protective constraint

It may challenge the **size of the implementation** while leaving the guarantee intact. "We need
audit logging" can be REDUCE on *which events are logged* while remaining BUILD on *logging at
all*. The question it is allowed to ask is: what is the smallest thing that keeps the guarantee
whole?

It may not reduce coverage of the guarantee and present that as a smaller version of it.
Sampling 10% of an audit trail is not a smaller audit trail; it is a different, weaker
guarantee in a performance costume.

The full doctrine, including the out-of-scope list that overrides every other deletion rule in
that document, is [references/deletion.md](references/deletion.md). That list covers security
controls, authentication, authorization, encryption, input validation, audit trails, safety
interlocks, rate limits, circuit breakers, kill switches, data integrity constraints, privacy
and data-retention behaviour, consent flows, deletion rights, regulatory and contractual
obligations, and compatibility of an interface with callers you cannot enumerate. Rate limits,
circuit breakers, and kill switches are on it **whether or not an incident has already
happened** — a control with a clean record may be working, not idle.

### If you ever see it recommend deleting a protective control

**Treat it as a defect and report it.** Do not act on it.

The doctrine in [references/deletion.md](references/deletion.md) explicitly forbids that
recommendation, so producing it is a failure of the skill and not a judgement you should weigh.
The [PHI access audit log example](examples/safety-phi-access-audit-log.md) is the case built
around exactly this boundary: every surface signal points at deletion — zero reads ever, 30% of
write volume, a real latency cost, and only a vague "legal says" behind it — and the correct
answer is still to retain the protection in full and route the latency complaint to the
implementation. The [evaluation suite](eval/README.md) carries that case as a
standing regression guard for the same reason.

Nothing in this skill makes deleting a security, legal, privacy, safety, compliance, or
compatibility constraint acceptable, easier, or optional.

## Failure modes and troubleshooting

All four of these were observed or measured. Where the text explains *why* something happens rather
than *what* was seen, it says so.

### The skill does not load at all

If you launched the agent with `--safe-mode`, that is why: testing established that `--safe-mode`
suppresses skill discovery, so the skill is simply not found. No error is reported for a skill that
was never discovered, which is what makes this one confusing to debug. Drop the flag.

If it still does not load, check the two paths that look plausible and do not work: skills are
not discovered through `--plugin-dir`, and they are not discovered through a relocated
`CLAUDE_CONFIG_DIR`. Confirm the file is at `~/.claude/skills/requirement-zero/SKILL.md` and ask
the agent to list its skills.

### A headless run returns nothing

Observed while testing this skill headlessly: a run with a low `--max-turns` ended in
`error_max_turns` with an empty result. The agent had reached a verdict and carried straight on into
*doing the work* — correct behaviour for an agent that just concluded BUILD — and ran out of turns
before returning anything. Scoping the request to the decision alone fixed it. So if you want the
verdict only, ask for the verdict and the scope lists and say that no implementation should follow.
Otherwise budget turns for the implementation you are implicitly asking for.

### The verdict label is noisier than the decision

Verdict labels blur at the DELETE/REDUCE boundary. In this project's own evaluation, on case 01
the model chose substantively the correct scope — it cut the entire proposed dashboard and
retained a single alert rule on a metric that already existed — and then labelled that outcome
**REDUCE** where the rubric expected **DELETE**. All six runs in the recorded matrix did this, in
both arms. Case 06 shows the same effect from the other side: the protective behaviour was
identical in every run of both arms, and the arms were separated only on the label.

The practical consequence: **treat the named deleted and retained scope as the reviewable output,
and the label as a summary of it.** If the two disagree, the scope lists are what you should act
on. This is a measured limitation, written up in
[eval/results/2026-08-15-claude-sonnet-4-6.md](eval/results/2026-08-15-claude-sonnet-4-6.md).

### Cost

The skill is not free. In the recorded evaluation the skill arm produced more output tokens than
the baseline (25,899 → 31,464 across 18 calls) and ran slower (mean 30.2 s → 36.4 s per call).
That is expected — the skill body is appended to the system prompt and the reasoning it demands
is longer prose — but it is real, and that evaluation measured **no** downstream saving to offset
it, because it has no implementation arm.

So: do not point it at a trivial request. Its value is entirely in the cases where the answer
turns out to be "build much less than you asked for", and a one-line change has no such answer to
find.

## Compatibility

Stated per host, with what was actually run. There is no "works everywhere" claim here.

### Claude Code — tested

Verified by installing into a skills directory with a plain `git clone` of the public repository,
with no install tooling, no package manager, and no configuration changes, then:

1. **Discovery.** Asked to enumerate the skills available to it, the agent listed
   `requirement-zero`.
2. **Triggering.** Given the log-parser plugin-system request above, the skill fired without being
   named and returned DEFER with the committed-second-consumer rule cited.
3. **Non-triggering, both boundaries.** The security request and the bug-fix request above were
   both correctly declined as out of scope, each citing the exclusion that the `description`
   frontmatter states.

Also established during that testing, and recorded here so nobody repeats it: skills are not
discovered via `--plugin-dir` or via `CLAUDE_CONFIG_DIR`; `~/.claude/skills/` is the path that
works.

### Codex and other Agent Skills-compatible hosts — NOT tested

**This has not been verified, and you should not assume it works.**

Why it was not tested: the Codex CLI was not installed in the environment this project was
developed in, and authenticating it required credentials that were not available. No run was
made, so there is no result to report — neither positive nor negative.

What makes portability *plausible* on inspection alone:

- The skill is a `SKILL.md` file: YAML frontmatter plus a Markdown body. Nothing else.
- There is no executable component — no script, no binary, no build step, no install hook.
- There is no tool dependency and no MCP server. The skill never needs to call anything.
- The `references/` files are reached by plain relative Markdown links from `SKILL.md`, so a host
  that resolves relative links in a skill directory gets progressive disclosure for free, and a
  host that does not still gets a self-contained skill body.

That is an argument from structure, not evidence. To actually verify it on another host, someone
would need to: install the directory wherever that host discovers skills; confirm the host lists
`requirement-zero` among available skills; issue the log-parser plugin request and check that a
verdict with itemized deleted and retained scope comes back; issue the credential-stuffing
request and the December off-by-one request and check that both are declined as out of scope; and
confirm that a `references/` link is resolvable from `SKILL.md` in that host. Reporting those
five results would replace this section with a tested one.

Until then: **untested**.
