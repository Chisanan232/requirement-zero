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
