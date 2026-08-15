---
id: build-hard-dispatch-optimizer
verdict: BUILD HARD
domain: logistics / core engine
---

# BUILD HARD — constrained dispatch optimizer

## Request

"We need a real routing optimizer: re-solve the whole city's assignment every 30 seconds under
time-window, cold-chain, and driver-certification constraints, in under two seconds, with
deterministic replay of every solve."

The product is same-day prescription delivery for independent pharmacies. Pharmacies pay us because
we hit a two-hour patient window more cheaply than a dedicated courier.

## Provenance

Proposed by the founding engineer and immediately challenged in review as over-engineering:
"just assign each order to the nearest available driver — we can optimise later." That challenge
is the correct instinct and it is wrong here, so it is worth answering with numbers rather than
architecture taste.

## Fundamental objective

Deliver a refrigerated, sometimes controlled prescription inside the patient's window, at a cost
per delivery below what we charge. Both halves are the objective. Hitting the window at a loss is
not a business, and being cheap while missing windows loses the pharmacy contract.

## Evidence

- **Present evidence, measured in a six-week pilot on the greedy nearest-driver version:**
  - On-time inside the two-hour window: **71%**. Contracts require 95%; two of five pilot
    pharmacies invoked the SLA clause.
  - Stops per completed route: **3.1**. Fully-loaded cost per delivery **$11.20** against a
    **$6.50** price. Gross margin is negative on every order.
  - Nine cold-chain excursions — items held above 8 °C beyond the 90-minute out-of-fridge budget our
    cold-chain policy allows. That budget is our own contractual commitment to the pharmacies and is
    stricter than most product labels require; breaching it means a discarded prescription, a
    re-dispense, and a reportable event under the BAA.
  - Four controlled-substance orders routed to drivers without the required certification and
    manually re-assigned. The chain-of-custody exposure here is the kind that ends a pharmacy
    relationship.
- **Constrained solve on the same pilot data, replayed offline:** 7.4 stops per route,
  cost per delivery **$5.10**, on-time **96%**, zero certification violations. The margin only
  exists at that route density, and that density is not reachable by assigning orders one at a time
  as they arrive — it requires deciding several orders together, and revising earlier decisions when
  a later order makes a better route possible.
- **If nothing hard is built:** the product is a courier service with negative unit economics and a
  71% hit rate. There is no version of the business that survives that. The difficulty is not
  incidental to the mission; the difficulty *is* the mission. Any competitor can drive a package
  across town — the reason a pharmacy signs with us is the density and the compliance guarantees,
  and both are produced by the solver.
- **The cheap alternatives were priced, not dismissed:** off-the-shelf routing APIs were evaluated
  and rejected on two hard requirements they do not express — the per-item cold-chain budget that
  starts when the item leaves the fridge (not when the route starts), and driver certification as a
  hard assignment constraint. Without those the output is not merely suboptimal, it is
  non-compliant.

## Verdict

**BUILD HARD.** This is a capacitated vehicle-routing problem with time windows plus per-item
perishability and certification constraints, re-solved continuously under a two-second budget. It
needs a genuine metaheuristic, hand-modelled constraints, and deterministic replay for dispute and
audit. It is the most expensive thing on the roadmap and it must not be simplified away.

Simplifying it to greedy assignment does not make the product smaller. It makes the product a
different, unprofitable, non-compliant product that happens to have less code.

## Scope deleted

BUILD HARD is not permission to build everything nearby. These were removed in the same pass:

- Live animated map of drivers for the pharmacy portal (nice, not load-bearing; pharmacies asked for
  an ETA, which is one field)
- Learned ETA model — the solver's own travel-time estimates are within tolerance and an ML pipeline
  here would be novelty rather than value
- Multi-city and multi-region generalisation before the second city exists
- Driver-preference learning and gamified scoring
- A configurable constraint DSL. Constraints are hand-written; there is one solver, one operator of
  it, and a DSL would be an abstraction over a single caller.

## Scope retained

- One solver for one city, with the four hard constraints modelled explicitly: patient time window,
  per-item cold-chain budget, driver certification class, driver shift end
- A 30-second re-solve loop with a two-second budget and a best-so-far fallback, so a slow solve
  degrades to the previous good assignment rather than to no assignment
- Seeded, deterministic replay of any solve from its recorded inputs — required to answer "why did
  this prescription arrive late" for a pharmacy and a regulator
- Continuous measurement of the four numbers that justified the build: on-time rate, stops per
  route, cost per delivery, constraint violations

## Next action

Build the constrained solver against the recorded pilot dataset as the acceptance test: it must
reproduce ≥7 stops per route and zero certification violations on data where the greedy version
scored 3.1 and four. Do not ship on top of the greedy assigner as a fallback path — two dispatch
strategies in production means the compliance guarantee is only sometimes true.
