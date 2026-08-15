# Mission Alignment and Necessary Difficulty

Load this when a requirement survives DELETE and the question is whether it is core, adjacent, or
mission-critical difficulty that must not be simplified away.

This file exists because the common failure of a subtraction-first practice is not over-building —
it is refusing to build the one expensive thing that the system's value depends on. A discipline
that only ever shrinks scope is a bias with good branding.

## Identifying the core value

Answer before judging any requirement: **what is the one thing this system must do well, such
that doing it badly makes everything else worthless?**

For a payments system, settling money correctly. For a search product, result relevance. For a
database, durability. For a coding agent, producing changes that work. Everything else — the
admin UI, the reporting, the second integration, the theming — is adjacent, however loudly it is
requested.

If the core value cannot be stated in one sentence, that is the first thing to resolve; without
it, FOCUS has no reference point and every verdict collapses to a size preference.

## Classifying a surviving requirement

Ask: does the outcome move the core value, or does it sit next to it?

| Case | Verdict |
|---|---|
| Moves the core value; cheap version suffices | BUILD, at the step 4 size |
| Moves the core value; cheap version provably fails | BUILD HARD |
| Adjacent, real evidence, blocking someone now | BUILD, minimal, and say it is adjacent |
| Adjacent, real value, nobody blocked | DEFER with a named trigger |
| Adjacent, no evidence | DELETE |

Adjacent work is not forbidden — it is ranked. Saying "this is adjacent, here is the two-hour
version" is a legitimate outcome and more useful than a refusal.

## The BUILD HARD bar

BUILD HARD requires all four:

1. The outcome is core by the definition above.
2. You considered a specific simpler version and can name it.
3. That simpler version fails the outcome for a reason you can state — a physical limit, a
   correctness property, a measured number, a regulatory guarantee, a scale threshold.
4. The failure is not merely aesthetic, inconvenient, or a matter of taste.

If you cannot name the rejected simpler version, you have not earned BUILD HARD; you have an
unexamined proposal. Go back to step 4.

## Difficulty that is legitimately irreducible

These recur, and each is a case where the cheap version is genuinely a different product:

- **Correctness under concurrency** — exactly-once semantics, distributed transactions,
  idempotency for money movement. "Just retry" produces double charges.
- **A hard performance floor** — a latency or throughput number below which the product does not
  function, not one that would be nice to hit.
- **Security and cryptographic guarantees** — key handling, isolation between tenants, auth
  boundaries. The simple version leaks.
- **Data durability and migration integrity** — losing or corrupting existing customer data is
  not recoverable by shipping a fix afterwards.
- **The core algorithm or model quality** — where the product *is* the quality of the output.
- **Regulatory guarantees with audit consequences** — the obligation defines the bar, not you.

Recognizing one of these is not a licence to skip DELETE. Run the parts test first: even
mission-critical work carries removable scope, and BUILD HARD applies to the irreducible core,
not to everything shipped alongside it.

## Difficulty that only looks necessary

Distinguish irreducible difficulty from difficulty you chose:

- Complexity from anticipated future requirements → not necessary. DEFER the anticipation.
- Complexity from an abstraction layer added for symmetry → not necessary. See `deletion.md`.
- Complexity from supporting a configuration nobody runs → not necessary.
- Complexity from a scale target with no evidence behind the number → challenge the number first;
  a made-up scale target manufactures real difficulty.
- Complexity inherited from a framework choice → real cost, but it is a dependency question, not
  a requirement question. Name it separately.

The test: does the difficulty come from the outcome itself, or from a decision made on the way to
the outcome? Only the former is BUILD HARD.

## Stating a BUILD HARD verdict

Include: the core value it serves, the simpler version rejected, the specific way it fails, and
the scope still deleted around the hard core. A BUILD HARD verdict with no deleted scope usually
means step 2 was skipped.

Do not soften it. If the honest answer is that this is six weeks of difficult work and there is no
shortcut, say that. Understating cost to seem agreeable is the same failure as building
unnecessary scope, one step later.
