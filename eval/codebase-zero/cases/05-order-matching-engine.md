---
id: 05-order-matching-engine
expected_verdict: INVEST
case_type: mission-critical-complexity-deserves-more-investment
example: ../../../skills/codebase-zero/examples/invest-matching-engine.md
guard: mission-critical-subsystem-not-simplified-away
---

## The artifact

`matching/` — 4,100 lines: the order book, a price-time priority implementation, a partial-fill state
machine, and a hand-written serialization layer written because the generic one was too slow.

## The request that prompted this audit

A quarterly engineering-health review ranked subsystems by maintenance cost. `matching/` came first
on every axis: highest churn, most defects, highest cyclomatic complexity, slowest tests, and the
subsystem engineers most often describe as "the scary part". The review asks what should be done
about it.

## What the system is for

An exchange. It matches buy and sell orders. If matching is incorrect or too slow, nothing else
about the product matters.

## Facts available

- Every order submitted to the system reaches this subsystem.
- `git log --diff-filter=A -- matching/` reaches the first commit in the repository.
- `git log --oneline -- matching/` contains three simplification attempts that were reverted. Two
  revert messages name incorrect fills found in staging; the third names a latency regression.
- p99 matching latency is measured continuously and quoted to customers. It currently sits close to
  the threshold below which large customers reroute their order flow elsewhere.
- The defect history is concentrated in the partial-fill state machine rather than spread across the
  subsystem.
- The tests are the largest and slowest in the suite and include property-based tests over concurrent
  submission orderings.
- The hand-written serialization layer has a benchmark in the repository showing it is measurably
  faster than the generic alternative.
- Incorrect fills are executed trades. They cannot be undone by deploying a fix.
