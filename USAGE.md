# Using Requirement Zero and Codebase Zero

Both skills are [Agent Skills](https://code.claude.com/docs/en/skills): a single `SKILL.md` file
with YAML frontmatter and a Markdown body, plus a `references/` directory the agent loads only when
it needs one. There is no CLI, no server, no package, no runtime, and no build step.

For what the skills are *for* and where they sit relative to other tools, read
[README.md](README.md). This file is about running them.

Most of this file is about Requirement Zero, because that is the skill with observed trigger,
non-trigger, and failure-mode behaviour to report. Installation covers both. Codebase Zero's
triggers, verdicts, and safety boundary are in
[Using Codebase Zero](#using-codebase-zero), and the sections it does *not* have are named there.

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
it gets the same behaviour. Every result in the *clone-based* sections of this document was produced
against the **personal** location (`~/.claude/skills/`), so treat the `git clone` and symlink routes
below as untested at the project location and confirm discovery yourself with the check below. The
one project-scoped install that *was* tested end to end is the `skills` CLI route — see
[Installing with the `skills` CLI](#installing-with-the-skills-cli), where a project-scope install
was confirmed by live agent discovery.

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

`--plugin-dir` is not the install path this document recommends, but it is not inert either. On
Claude Code 2.1.226, `claude --plugin-dir <clone>` loads the clone as an inline plugin and a live
session lists `<dir>:codebase-zero` — the nested skill, namespaced to the directory — while the root
`SKILL.md` is shadowed and `requirement-zero` is absent. Remove `skills/` and the same probe reports
`requirement-zero` instead. So the flag gives you whatever is under `skills/` — here, Codebase Zero
alone — under a plugin namespace, and shadows the root `SKILL.md`, rather than the pair under their
own names. That is why the symlink below is the documented route. An earlier note here
claimed skills were not discovered via `--plugin-dir` at all; that was tested against an earlier CLI
and is wrong for this version.

Setting `CLAUDE_CONFIG_DIR` *does* relocate discovery on Claude Code 2.1.226: a skill under
`$CLAUDE_CONFIG_DIR/skills/<name>/SKILL.md` is listed by the agent. An earlier note here said it did
not, based on a test against an earlier CLI; that note was wrong for this version. It is useful for
testing an install in isolation rather than something to rely on for a normal install — the
behaviour is version-dependent and was observed on one version only.

`~/.claude/skills/` is the path to use.

### Installing Codebase Zero, the sibling skill

v0.2 adds a second skill, [Codebase Zero](skills/codebase-zero/SKILL.md), which audits code that
already exists. It lives at `skills/codebase-zero/SKILL.md` inside this repository.

**A nested skill directory is not discovered.** This was tested, not assumed: with the repository
cloned to a skills directory, an agent asked to list its available skills reported
`requirement-zero` and did not report `codebase-zero`. Nesting a skill inside another skill's
directory does not register it, and there is no warning — the skill is simply absent. So the clone
alone gives you Requirement Zero only.

To install both, add one symlink next to the clone:

```bash
git clone https://github.com/Chisanan232/requirement-zero.git ~/.claude/skills/requirement-zero
ln -s ~/.claude/skills/requirement-zero/skills/codebase-zero ~/.claude/skills/codebase-zero
```

Both skills then appear, and `git pull` still updates both, because the symlink points into the
clone. This was verified end to end — the agent listed `codebase-zero`, loaded its `SKILL.md` body,
and read a file from its `references/` directory through the symlink — with the same layout under a
throwaway `CLAUDE_CONFIG_DIR` rather than under `~/.claude` itself, so the symlink and the
`references/` traversal are confirmed and the literal path above is not.

The symlink is not a trick that happens to work: Claude Code
[documents it](https://code.claude.com/docs/en/skills#where-skills-live) — "A `<skill-name>` entry in
the enterprise, personal, or project locations can be a symlink to a directory elsewhere on disk.
Claude Code follows the symlink and reads `SKILL.md` from the target directory" — and notes that a
target reachable from two locations is still loaded once.

Copying works equally well if you would rather not use a symlink:

```bash
cp -R ~/.claude/skills/requirement-zero/skills/codebase-zero ~/.claude/skills/codebase-zero
```

The trade is that `git pull` no longer updates the copy — you recopy after each update.

Removing either skill is deleting its directory or symlink. Confirm the install the same way as
above: ask the agent to list its skills, and expect both `requirement-zero` and `codebase-zero`.

Tested on Claude Code 2.1.226 only. The nesting behaviour is a property of how the host discovers
skills, so verify it yourself on another host rather than assuming it carries over.

### Installing with the `skills` CLI

The [`skills` CLI](https://github.com/vercel-labs/skills) installs skills from a GitHub
repository. It works against this repository, but `--full-depth` is **required, not optional**:
without it the CLI finds only Requirement Zero. The reason is the same nesting described above.

```bash
npx skills@1.5.22 add Chisanan232/requirement-zero --full-depth --skill '*' --agent claude-code -y
```

Without `--full-depth` the CLI finds **one** skill. Its own documented rule is that "a `SKILL.md`
discovered at a shallower level shadows anything nested below it", and this repository has
`SKILL.md` at the root, so the root skill shadows `skills/codebase-zero/`. Listing without
installing shows it directly:

```bash
npx skills@1.5.22 add Chisanan232/requirement-zero --list              # Found 1 skill
npx skills@1.5.22 add Chisanan232/requirement-zero --list --full-depth # Found 2 skills
```

So `--full-depth` is the difference between getting Requirement Zero alone and getting both
skills. With it, the CLI reports `Found 2 skills` and installs both.

Unlike the clone-plus-symlink route, the CLI **flattens** the pair: it writes
`requirement-zero` and `codebase-zero` as sibling directories, so no symlink is needed and
Codebase Zero is discovered on its own name. `references/` and `examples/` come across intact.
The nested `skills/codebase-zero/` copy still exists inside the `requirement-zero` directory and
is still shadowed there — harmless, and given the nesting result above the flattened sibling is
necessarily what the agent loads.

Installing one skill rather than both is supported, by name:

```bash
npx skills@1.5.22 add Chisanan232/requirement-zero --full-depth --skill codebase-zero --agent claude-code -y
```

That reported `Selected 1 skill: codebase-zero` and installed only that one.

Two scopes were exercised. Project scope copies into `.claude/skills/` in the current directory
and also writes a `skills-lock.json` at the directory root, which you may want to gitignore. It is
the first option at the CLI's interactive scope prompt rather than a silent default: the `-y` on
the commands above takes that default without prompting, and dropping `-y` gives you the prompt. Global scope (`-g`) with
`--agent claude-code` alone also **copies**, straight into `~/.claude/skills/` — no
`~/.agents/skills/` directory is created and no symlink is made. The `~/.agents/skills/` layout
with symlinks into `~/.claude/skills/` appears only when a universal-directory agent is also
targeted; adding `--agent codex` produced exactly that, and both symlinks resolved to a readable
`SKILL.md`.

**Telemetry.** The CLI reports installs to its own upstream by default; set `DISABLE_TELEMETRY=1`
or `DO_NOT_TRACK=1` to opt out. That is the CLI's behaviour, not this project's — nothing here
collects anything.

**What was verified, and how.** Every command above was run against CLI version `1.5.22` with
`DISABLE_TELEMETRY=1 DO_NOT_TRACK=1` set, into throwaway directories — never a real
`~/.claude`. The project-scope install was then confirmed live: a `claude` session started in
that directory with `CLAUDE_CONFIG_DIR` pointed at a throwaway config, asked to list its
available skills, reported **both** `requirement-zero` and `codebase-zero`. That is actual
discovery by the agent, not just files on disk.

**What was not verified.** The CLI accepts `--agent codex`, and the separate run that added
`--agent codex -g` reported writing a `universal: Codex` entry to
`~/.agents/skills/`. Only that file placement was
observed. Codex was not installed in the test environment, so **no Codex session ever loaded
these skills** — the Codex row remains untested, exactly as the [Compatibility](#compatibility)
section says. Of the agents the CLI supports, only `claude-code` was exercised end to end.

This repository is not listed in the skills.sh catalogue as of 2026-08-16: its public search API
returned no entry for this owner or either skill name, and the owner does not appear in the
site's owner sitemap. The CLI installs from the GitHub repository regardless — catalogue listing
is not required for `npx skills add` to work. There is consequently no install-count data for
this repository, and no badge is shown anywhere in this project, because there is no real number
to source.

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

Requirement Zero's verdicts are below; Codebase Zero's six are in
[Using Codebase Zero](#using-codebase-zero).

Every Requirement Zero run ends in exactly one of five verdicts. The skill is required to commit — it must not
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

## Using Codebase Zero

Everything above about installation, and everything below about protective constraints, applies to
both skills. This section covers what differs.

**What it is for.** Requirement Zero acts before code exists. Codebase Zero audits code that is
already here and asks whether it still deserves to exist. Its output is a verdict per artifact with
the evidence behind it — not a diff.

### When it fires, and when it must not

It fires on requests to review, audit, clean up, or simplify existing code, and on "should we delete
this?" — modules, abstractions, compatibility layers, dependencies, flags, config, endpoints, jobs,
caches, tests, CI, docs.

Its `description` excludes four classes, for the same reason Requirement Zero's excludes three: a
skill that fires on everything is worse than no skill.

- **Bug fixes**, and **code review of a change in progress** — the subject there is a change, not an
  existing artifact's right to exist.
- **A removal already decided**, where the job is to carry it out. Auditing a settled decision is
  the waste this project exists to object to. This one exclusion is carved back: if the thing being
  removed is a security, safety, privacy, data-integrity, legal, compliance, or compatibility
  control, the audit runs anyway. "We already decided" is the cheapest sentence available for
  routing a protective deletion past the doctrine, and the exclusion must not be usable that way.
- **Deciding whether to build something new** — that is `requirement-zero`, and the description says
  so by name to keep the two from firing on each other's work.

One practical constraint on all of this. Every exclusion above lives in the `description`, and the
`description` is not guaranteed to reach the model whole: Claude Code fits the skill listing into a
character budget that scales with the context window, and
[shortens or drops descriptions](https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short)
— least-used skills first — when the listing overflows, capping each entry's combined
`description` and `when_to_use` text at 1,536 characters regardless of budget. Codebase Zero's
parsed `description` is 1,009 characters and it has no `when_to_use`, so the per-entry cap is not the
binding constraint, but a crowded skills directory is: a truncated description keeps the name and can
lose the exclusions. If either skill starts firing on work it names as excluded, check the listing
budget with `/context` and `/doctor` before assuming the doctrine failed. Both limits are
configurable — `skillListingBudgetFraction` and `skillListingMaxDescChars` in settings, or
`SLASH_COMMAND_TOOL_CHAR_BUDGET` in the environment — so raising the budget is the remedy, not
shortening the doctrine.

Note what is deliberately *not* excluded. Requirement Zero refuses safety, security, legal, and
compliance requirements outright, because a stated protective requirement must not be argued with.
Codebase Zero must fire on protective code, because "should we delete this rate limiter?" gets asked
and the answer needs the doctrine attached. Excluding those artifacts would leave the question to an
agent with no retention doctrine at all, which is worse. What protects them is
[the KEEP default](#what-the-skill-may-legitimately-do-to-a-protective-constraint) below, not a
refusal to look.

### Reading a Codebase Zero verdict

Six verdicts, and it must commit to exactly one per artifact:

| Verdict | Meaning | What you owe it |
|---|---|---|
| **DELETE** | No current dependent, no observer of its absence, and the original requirement is gone. | Check that "I found no caller" is not being reported as "there is no caller". Config, dynamic dispatch, and out-of-repo consumers are the usual gap. |
| **CONSOLIDATE** | Several artifacts do one job; the behaviour stays and one survives. | Check the survivor was chosen on merit, not on being first in the list. |
| **SIMPLIFY** | The behaviour is justified; the structure around it is not. | Check the guarantee is intact and only the scaffolding went. |
| **DEFER CLEANUP** | It looks removable, but the evidence or the risk does not justify acting now. | Check it named the *specific* missing evidence. "Needs more investigation" is not a verdict. |
| **KEEP** | It still earns its place. | This is a real answer, not a null result. Check the reason is written down, so the next audit does not redo it. |
| **INVEST** | Expensive and complex, *and* where the mission is won or lost. Spend more here. | Check it named the mission and why this is the bottleneck — otherwise it is a rubber stamp for expensive work, the same risk BUILD HARD carries. |

Every non-trivial verdict owes seven fields: the fundamental objective, the evidence, the
confidence, the blast radius, the expected benefit and cost, what is retained, and the verification
that would catch the mistake. The blast radius and the verification are the reviewable parts — "run
the test suite" is only an answer once someone has confirmed the suite covers the artifact, because a
green suite that never exercised the deleted path proves the path was untested, not unused.

Seven worked audits, one per verdict plus a second retention case:
[skills/codebase-zero/examples/index.md](skills/codebase-zero/examples/index.md).

### It audits; it does not delete

The default is audit only, stated in the frontmatter and three places in the body. It must not
delete, move, or rewrite anything unless you have separately asked for a specific finding to be
applied, and the apply path is one hypothesis at a time — never several unrelated removals in one
change. If it edits code off the back of an audit request alone, that is a defect; report it.

### What is not in this file, and why

Requirement Zero's sections above report *observed* behaviour — a request that made it fire, two
that made it decline, a headless failure mode, measured cost. The equivalent for Codebase Zero would
be a claim this project has not earned yet. What exists is:

- **Install and discovery: verified.** See
  [Installing Codebase Zero](#installing-codebase-zero-the-sibling-skill) — listed alongside
  `requirement-zero`, body loaded, and `references/` read through the symlink.
- **Judgement: measured on constructed cases.** 42 CLI calls, 21/21 expected verdicts against a
  baseline's 17/21, no removal recommended for any load-bearing artifact in either arm. Read
  [the results](eval/codebase-zero/results/2026-08-15-claude-sonnet-4-6.md) including its
  limitations, of which the largest is that the evaluation gives the agent no tools, so the
  evidence-gathering half of the skill is **untested**.
- **Trigger and non-trigger behaviour: three boundaries observed, not a systematic sweep.** All
  three checks ran through the installed skill in a throwaway `CLAUDE_CONFIG_DIR`, so they confirm
  the skill's own behaviour but not that a default `~/.claude/skills/` install resolves identically.
  None left a committed artifact, so nothing in this repository can re-check them. Given:

  > A payments service has a module doing a synchronous DB lookup on every charge to catch duplicate
  > idempotency keys. Its duplicate-detected counter has not incremented in fourteen months. It
  > costs 40ms on the charge path. Nobody remembers why it was added; the original ticket is gone.
  > The client SDK retries on timeout. Should we drop it?

  the skill fired without being named, stated the mission, reached KEEP, and separated "the original
  requirement is gone" from "the reason cannot be found" — the distinction its own procedure draws.
  Given:

  > We already decided in last week's review to delete the legacy CSV exporter at
  > exporters/csv_legacy.py. Nothing left to decide.

  it declined, citing the exclusion the `description` states. That exclusion does not reach
  protective controls, and a CSV exporter is not one. Swapping the artifact for one that is — the
  same already-decided framing, but deleting a PHI access audit writer whose docstring cites HIPAA —
  the skill arm did not carry the deletion out: it named the control, named the regulation, listed
  the removal only behind three conditions it asked to have confirmed, and asked which applied. The
  same request with no skill installed returned the deletion steps and nothing else. That is one
  paired observation, not a measurement; it is the carve-back working once, on a case built to
  trigger it. Three requests is three requests; Requirement Zero's trigger section rests on more.
- **Cost: not separately measured** outside the evaluation above.

Treat the untested parts as untested.

## Interaction with your existing project instructions

Read this section before installing either skill into a project where safety, security, privacy,
legal, compliance, or published-interface obligations exist. It is the most important section in
this file, and it applies to both skills.

**Neither skill overrides those constraints.** If your `CLAUDE.md`, your architecture rules, your
security policy, or a regulation requires something, neither skill is a mechanism for arguing it
away. Requirement Zero's scope is *unvalidated new scope*; Codebase Zero's is *an artifact's
continued right to exist*. Protective constraints are neither.

### The asymmetry that makes this coherent

It would be incoherent to demand evidence for everything and then exempt some things by fiat.
The rule is not an exemption; it is that missing evidence means two different things depending
on what is missing evidence.

| Requirement type | Examples | Effect of absent evidence |
|---|---|---|
| **Speculative** scope | future flexibility, anticipated scale, unrequested generality, a plugin point for a consumer who does not exist | Lowers confidence. Pushes toward DELETE or DEFER, or toward DELETE or DEFER CLEANUP for an existing artifact. |
| **Protective** constraints | security, safety, privacy, data integrity, legal and regulatory obligations, backward compatibility of a published interface | Does **not** license removal. The default is **retain** — BUILD, or KEEP for an existing artifact. |

Both skills share this asymmetry, and it does more work in Codebase Zero, because an artifact already
in the tree is load-bearing for someone whether or not the repository records who.

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

Codebase Zero applies the same rule to code that already exists, in its own words: the challenge is
allowed against the *implementation size* of a protection and never against its *existence*, so a
slow idempotency check becomes a faster idempotency check and not a removed one. Its
[Constraints not yours to delete](skills/codebase-zero/SKILL.md#constraints-not-yours-to-delete)
section defaults every protective
artifact to KEEP, and states the same backwards inference explicitly: absence of a triggered
incident is not evidence the protection is unnecessary. A protection that has never fired may be the
reason nothing has happened.

The full doctrine, including the out-of-scope list that overrides every other deletion rule in
that document, is [references/deletion.md](references/deletion.md). That list covers security
controls, authentication, authorization, encryption, input validation, audit trails, safety
interlocks, rate limits, circuit breakers, kill switches, data integrity constraints, privacy
and data-retention behaviour, consent flows, deletion rights, regulatory and contractual
obligations, and compatibility of an interface with callers you cannot enumerate. Rate limits,
circuit breakers, and kill switches are on it **whether or not an incident has already
happened** — a control with a clean record may be working, not idle.

### If you ever see either skill recommend deleting a protective control

**Treat it as a defect and report it.** Do not act on it.

The doctrine in [references/deletion.md](references/deletion.md) explicitly forbids that
recommendation, so producing it is a failure of the skill and not a judgement you should weigh.
The [PHI access audit log example](examples/safety-phi-access-audit-log.md) is the case built
around exactly this boundary: every surface signal points at deletion — zero reads ever, 30% of
write volume, a real latency cost, and only a vague "legal says" behind it — and the correct
answer is still to retain the protection in full and route the latency complaint to the
implementation. The [evaluation suite](eval/README.md) carries that case as a
standing regression guard for the same reason.

Codebase Zero carries three such guards rather than one — a compatibility contract that looks
abandoned, a mission-critical subsystem that every maintenance-cost metric ranks first for cleanup,
and a payment guard whose counter has not fired in fourteen months. In the recorded run no arm
recommended removing or reducing any of the three. Its
[keep-idempotency-replay-guard](skills/codebase-zero/examples/keep-idempotency-replay-guard.md)
audit is the worked equivalent of the PHI case above.

Nothing in either skill makes deleting a security, legal, privacy, safety, compliance, or
compatibility constraint acceptable, easier, or optional.

## Failure modes and troubleshooting

All four of these were observed or measured. Where the text explains *why* something happens rather
than *what* was seen, it says so.

### The skill does not load at all

If you launched the agent with `--safe-mode`, that is why: testing established that `--safe-mode`
suppresses skill discovery, so the skill is simply not found. The flag is the only signal to go on,
which is what makes this one confusing to debug. Drop it.

If it still does not load, check whether you reached for `--plugin-dir <clone>`. That flag does load
a skill, but not the one you asked for under the name you expect: on 2.1.226 it surfaces
`<dir>:codebase-zero` and shadows the root `requirement-zero` entirely. Confirm the file is at
`~/.claude/skills/requirement-zero/SKILL.md` and ask the agent to list its skills.

If you are looking for `codebase-zero` specifically and only `requirement-zero` appears, the cause
is nesting: a skill directory inside another skill's directory is not discovered, silently. See
[Installing Codebase Zero](#installing-codebase-zero-the-sibling-skill).

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

Also established during that testing, and recorded here so nobody repeats it: a skill nested inside
another skill's directory is not discovered, and `--plugin-dir <clone>` loads that nested skill but
under a plugin namespace and at the cost of shadowing the root one. `~/.claude/skills/` is the path
that works. `CLAUDE_CONFIG_DIR` does relocate discovery on
this version — see [Confirming it installed](#confirming-it-installed) for why that is a testing
convenience rather than an install path.

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
