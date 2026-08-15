# Worked examples

Six decisions, one per file. They exist to show that Requirement Zero operates on the requirement —
before design, before code — and that it reaches a real verdict in both directions: build nothing,
and build the hard thing properly.

These are documentation and evaluation fixtures. They are **not** loaded at skill runtime; `SKILL.md`
stays compact deliberately.

## The corpus

| Example | Verdict | Shows |
|---|---|---|
| [Pipeline health dashboard](delete-assumed-dashboard.md) | **DELETE** | Nothing proposed survives; the real need is met by an alert that already had its metric |
| [Payment provider plugin architecture](reduce-plugin-architecture.md) | **REDUCE** | Abstraction generalised from one implementation, cut to three functions |
| [Enterprise white-label theming](defer-enterprise-white-label.md) | **DEFER** | No consumer, no date, expensive-to-reverse design; parked with a trigger |
| [CSV import error report](build-csv-import-recovery.md) | **BUILD** | Evidenced current failure; smallest sufficient version, adjacent scope cut |
| [Constrained dispatch optimizer](build-hard-dispatch-optimizer.md) | **BUILD HARD** | Difficulty is the mission; simplifying it produces a product that cannot work |
| [PHI access audit log](safety-phi-access-audit-log.md) | **BUILD** (safety guard) | A protection is not deleted for lack of a convenient justification |

If you read two, read [the DELETE case](delete-assumed-dashboard.md) and
[the BUILD HARD case](build-hard-dispatch-optimizer.md). They are the two ends of the range.

## Structure

Every example uses the same headings in the same order, so they can be parsed as fixtures:

```
frontmatter    id, verdict, domain (+ guard, where the case is a regression guard)
# <title>                the H1 is prose; read the verdict from frontmatter, never from here
## Request               the requirement as it actually arrived
## Provenance            who created it, what authority is claimed, what that traces back to
## Fundamental objective the underlying job, restated free of the proposed solution
## Evidence              present evidence vs imagined future, and what breaks if nothing is built
## Verdict               exactly one of DELETE / REDUCE / DEFER / BUILD / BUILD HARD
## Scope deleted         named explicitly, including "nothing" and why
## Scope retained        what survives
## Next action           the single next step
```

The eight `##` sections above are mandatory and always in that order. Two examples add an optional
section: `## Trigger to revisit` before `## Next action` on the DEFER case, and a trailing note
after `## Next action` on the REDUCE and safety cases. A fixture parser can require the eight and
ignore anything after `## Next action`.

This file is the index, not a fixture: it has no frontmatter, which is how a parser globbing
`examples/*.md` should skip it.

## What these are meant to make clear

Requirement Zero sits in a neighbourhood of tools and prompts that also push back on unnecessary
work. The examples are the argument for where the line falls; the short version:

- **Code-level minimisers and deletion audits.** We have not verified the current behaviour of any
  specific project and make no claims about their features; what follows is about a *category*, and
  projects such as Ponytail and Void are the ones usually named in it. That category works on code
  that exists or has already been
  decided on: shrink this implementation, remove this dead path, flag this over-engineering. Useful
  work, one step later than this. In [the REDUCE case](reduce-plugin-architecture.md), a code-level
  pass over a well-built plugin architecture finds a clean, well-tested system and correctly reports
  nothing wrong. The problem is that it should never have been written.
- **Generic first-principles or persona prompting** ("think from first principles", "be a ruthless
  minimalist") produces a disposition rather than a decision. Requirement Zero terminates in one of
  five named verdicts with the deleted scope written down, which is a reviewable artifact.
- **Minimalism prompts** cannot produce [the BUILD HARD case](build-hard-dispatch-optimizer.md).
  Asked to keep things simple, they simplify the dispatch optimizer into greedy nearest-driver
  assignment and destroy the product's unit economics and its compliance guarantees while
  reducing the line count. A method that cannot say "this is hard and it stays hard" is an excuse to
  under-build.
- **Aggressive deletion** cannot produce [the PHI audit log case](safety-phi-access-audit-log.md).
  Every surface signal there points at deletion: no reads, no measurable use, real cost, and only
  "legal says" behind it. Absent justification is a trigger to research and escalate, not a licence
  to remove a protection.
