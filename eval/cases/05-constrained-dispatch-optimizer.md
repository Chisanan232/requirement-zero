---
id: 05-constrained-dispatch-optimizer
expected_verdict: BUILD HARD
case_type: mission-critical-complexity-retained
example: ../../examples/build-hard-dispatch-optimizer.md
---

## Requirement as filed

"We need a real routing optimizer: re-solve the whole city's assignment every 30 seconds under
time-window, cold-chain, and driver-certification constraints, in under two seconds, with
deterministic replay of every solve."

The product is same-day prescription delivery for independent pharmacies. Pharmacies pay for it
because it hits a two-hour patient window more cheaply than a dedicated courier does.

## Who filed it, and on what authority

Proposed by the founding engineer. Challenged in design review as over-engineering: "just assign
each order to the nearest available driver — we can optimise later."

## Facts available

Six-week pilot, run on the greedy nearest-available-driver version, in one city:

- On-time inside the two-hour patient window: 71%. Signed pharmacy contracts require 95%. Two of
  the five pilot pharmacies invoked the SLA clause.
- Stops per completed route: 3.1. Fully-loaded cost per delivery $11.20 against a $6.50 price.
  Gross margin was negative on every order.
- Nine cold-chain excursions: items held above 8 °C beyond the 90-minute out-of-fridge budget the
  company's own cold-chain policy commits to in its pharmacy contracts. That budget is stricter
  than most product labels require. A breach means a discarded prescription, a re-dispense, and a
  reportable event under the BAA.
- Four controlled-substance orders were assigned to drivers without the required certification and
  had to be re-assigned by hand.

Same pilot data, replayed offline through a constrained solve: 7.4 stops per route, cost per
delivery $5.10, on-time 96%, zero certification violations. The route density that produces the
margin comes from deciding several orders together and revising earlier assignments when a later
order makes a better route possible; assigning each order at arrival does not reach it.

Other facts:

- Off-the-shelf routing APIs were evaluated. None expresses a per-item perishability budget that
  starts when the item leaves the fridge rather than when the route starts, and none expresses
  driver certification as a hard assignment constraint.
- Pharmacies and regulators ask, after the fact, why a specific prescription arrived late.
- Also proposed in the same thread: a live animated driver map for the pharmacy portal (pharmacies
  have asked for an ETA), a learned ETA model, multi-city and multi-region generalisation, driver
  preference learning with gamified scoring, and a configurable constraint DSL. There is one city,
  one solver, and one person who operates it. The solver's own travel-time estimates are currently
  within tolerance.
