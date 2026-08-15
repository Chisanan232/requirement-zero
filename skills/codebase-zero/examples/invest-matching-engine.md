# INVEST — the order matching engine

**Artifact:** `matching/` — 4,100 lines across the order book, the price-time priority
implementation, the partial-fill state machine, and a hand-written serialization layer that exists
because the generic one was too slow. Highest churn in the repository, highest defect count, and the
subsystem every engineer describes as "the scary part".

## Mission

Match buy and sell orders correctly, at the speed the market requires. If matching is wrong or slow,
the product has no reason to exist.

## Objective the artifact serves

Maintain the order book and produce fills that respect price-time priority, under concurrent order
submission, without losing or duplicating an order.

## Origin

`git log --diff-filter=A -- matching/` reaches the first commit in the repository. This subsystem is
not accumulated history — it is the product. Later commits show three attempts to simplify it:
`git log --oneline -- matching/` includes two reverts whose messages name correctness failures found
in staging, and a third whose message names a latency regression.

## Evidence

- Every order path in the system reaches it. It is not merely referenced; it is the thing being
  referenced.
- Its tests are the largest and slowest in the suite, including property-based tests over concurrent
  submission orderings.
- Latency is measured and published internally: the p99 matching latency is a number the business
  quotes to customers, and it currently sits close to the threshold below which large customers
  reroute their flow.
- The defect history is concentrated in the partial-fill state machine, not spread across the
  subsystem.
- The hand-written serialization layer has a benchmark in the repository. It is measurably faster
  than the generic one. This is measured, not asserted.

## Confidence

High. The mission statement, the traffic, the measured latency threshold, and the revert history all
point the same way.

## Complexity class

**Essential.** Rebuild this tomorrow with perfect knowledge and no legacy, and price-time priority
under concurrency is still hard, partial fills still need a state machine, and the latency floor is
still a floor. The three reverted simplification attempts are direct evidence: two produced
incorrect fills, one was too slow. The cheap version is a different, worse product.

The one piece that is *not* essential: the serialization layer would be accidental complexity if the
benchmark did not exist. It does exist and it is favourable, so the complexity is bought rather than
assumed.

## Blast radius

Irreversible in the sense that matters: incorrect fills are trades that happened. A revert restores
the code and does not un-execute a trade. This is the strongest possible argument against casual
change, and equally the strongest argument for concentrating engineering effort here rather than
elsewhere.

## Benefit and cost

The p99 latency sits near the threshold where large customers reroute. The defect concentration in
the partial-fill state machine is where correctness incidents originate. Both are mission-limiting
right now. Engineering spent here changes what the product can sell; the same engineering spent on
the admin UI does not.

Cost is high and stays high: this work needs the strongest tests in the codebase and the most
careful review.

## Verdict: INVEST

**What is currently limited:** p99 matching latency against a threshold customers act on, and
correctness defects concentrated in one identifiable component.

**Expected improvement:** headroom against the latency threshold, and a partial-fill state machine
with exhaustive rather than incidental test coverage. Both are measurable — the latency number
already exists, and the defect rate is already tracked.

## Retained

Everything, including the hand-written serialization layer, which has earned its place by
measurement.

## Verification needed

For any change here: the property-based concurrency tests, the latency benchmark against the
published number, and review by someone who knows the subsystem. Not the standard gates alone.

## The mistake this case exists to prevent

Every maintenance-cost heuristic ranks this subsystem first for cleanup: most churn, most defects,
most complexity, most feared. Recommending that it be simplified would be the most expensive
possible output of an audit. High cost is not the same as unjustified cost. This is where the money
is made, and the correct recommendation is to spend *more* here — while still deleting removable
scope around the hard core, which INVEST does not exempt.
