# Accidental and Essential Complexity

Load this when an artifact is complex and the question is whether the complexity belongs to the
problem or to a decision someone made on the way to solving it.

This is the distinction the audit exists for. Everything else — reference counts, history, blast
radius — is procedure. This step is judgment, and getting it backwards is the failure that makes a
cleanup destroy the product instead of improving it.

## The test

**Does the difficulty come from the outcome itself, or from a choice made on the way to the
outcome?**

Essential complexity survives any reimplementation. Write the system again from scratch, with
perfect knowledge and no legacy, and the difficulty is still there — because it is the problem's
difficulty, not the code's. Accidental complexity disappears in that rewrite.

Ask concretely: if a competent team rebuilt this subsystem tomorrow knowing everything we now know,
would they hit this same wall? If yes, it is essential, and the verdict is KEEP or INVEST. If they
would take a straighter path, it is accidental, and the verdict is SIMPLIFY or CONSOLIDATE.

## Complexity that is essential

Each of these is a case where the simple version is a different, worse product. Recognizing one is
not permission to skip the audit — even essential subsystems carry removable scope around the hard
core.

- **Correctness under concurrency** — exactly-once semantics, distributed transactions, idempotency
  for money movement, ordering guarantees. "Just retry" produces double charges.
- **A hard performance floor** — a latency or throughput number below which the product does not
  function. Not a number that would be nice to hit; one that has been measured and is load-bearing.
- **Security and isolation guarantees** — key handling, tenant isolation, auth boundaries. The
  simple version leaks, and the leak is discovered by someone else.
- **Data durability and migration integrity** — corrupting existing customer data is not fixable by
  shipping a patch afterwards.
- **The core algorithm or model quality** — where the product *is* the quality of its output.
- **Regulatory guarantees with audit consequences** — the obligation sets the bar, not you.
- **Failure handling at a real trust boundary** — validation, timeouts, and backpressure at the edge
  where untrusted input or an unreliable dependency arrives. Defensive code inside a boundary you
  control is a different question.

## Complexity that only looks essential

These feel necessary from inside the code and are not:

- Structure built for anticipated future requirements. The anticipation is the artifact; SIMPLIFY.
- An abstraction layer added for symmetry with a neighbouring subsystem.
- Support for a configuration nobody sets, or a flag that has been on in every environment since it
  was added and whose off-branch no longer works.
- A scale target with no measurement behind the number. A made-up target manufactures real
  difficulty, and the fix is to challenge the number first.
- Genericity serving exactly one caller. One implementation of an interface is a concrete thing
  wearing a costume.
- Complexity inherited from a framework or dependency choice. Real cost, but it is a dependency
  question, not an essential-complexity one. Name it separately rather than treating it as
  irreducible.
- Layers that only forward: a service calling a manager calling a repository, each adding a
  signature and nothing else.

## CONSOLIDATE against SIMPLIFY

Both mean "the behavior stays, the structure shrinks". The difference is arithmetic.

- **CONSOLIDATE** — more than one artifact does substantially the same job, and one should survive.
  Two clients for the same API, three date-formatting helpers, a legacy and a current path that both
  still run, parallel implementations behind a flag that is now permanently on. Always name which
  one survives and why, and check whether the survivors' behaviors are actually identical — a
  duplicate that quietly diverged is two behaviors, and merging them changes one of them.
- **SIMPLIFY** — one artifact, internally larger than its job. An abstraction with one
  implementation, an unreached branch, a cache nobody measured, a configuration surface nobody uses,
  a queue for work that is not asynchronous.

Where both apply, consolidate first and then simplify the survivor. Simplifying two artifacts you
are about to merge is work done twice.

## The bar for INVEST

INVEST requires all four. Without all four it is KEEP, which is a perfectly good verdict and does
not need dressing up.

1. The artifact serves the mission as stated at the start of the audit — not adjacent value,
   however real.
2. It is currently the bottleneck: the thing whose quality, speed, or correctness limits the
   product right now. Name what is limited, and how you know.
3. The complexity is essential by the test above, so the effort cannot be avoided by simplifying.
4. More engineering here would produce a proportionate outcome. State what improvement, and what
   would show it.

INVEST is what stops this skill from being a code shrinker. A subsystem can be the ugliest, most
expensive, highest-churn thing in the repository and still be exactly where the next three months
should go. Recommending its deletion because it scores badly on maintenance cost is the most
expensive mistake this audit can make.

State an INVEST verdict with the same seven fields as any other, and add what is currently limited
and what improvement is expected. Do not soften the cost: if the honest answer is that this is hard
and will stay hard, say that.

## Ordering, when several verdicts apply

An audit usually produces a mix. Sequence them so earlier work is not wasted:

1. DELETE first — deleting removes the need to simplify anything.
2. CONSOLIDATE second — merge before improving the survivor.
3. SIMPLIFY third — on what remains.
4. INVEST alongside, on the core, and never as a substitute for the first three. Optimizing a
   subsystem that still contains three dead layers means optimizing the dead layers too.

DEFER CLEANUP and KEEP produce no work now. Say what would change them, and stop.
