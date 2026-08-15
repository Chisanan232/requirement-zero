---
id: 02-payment-provider-plugin-architecture
expected_verdict: REDUCE
case_type: much-smaller-solution-is-correct
example: ../../examples/reduce-plugin-architecture.md
---

## Requirement as filed

"Before we add Stripe billing, build a payment provider plugin architecture: a `PaymentProvider`
interface, a provider registry, per-provider config schemas, dynamic loading from
`providers/*.py`, and a conformance test suite every provider must pass."

## Who filed it, and on what authority

Proposed by the engineer who will implement billing, and endorsed in design review with
"architecture requires that we not couple ourselves to a vendor." Asked which document says so:
no architecture document mentions payment providers. The phrase traces to an internal
engineering-principles page about avoiding vendor lock-in.

## Facts available

- The product will take payment through one processor (Stripe), in one currency, through one
  checkout flow. The only operations the product performs against it are charge, refund, and
  webhook reconciliation.
- A second processor for local EMEA payment methods appears in a sales deck as a possibility for
  enterprise customers. No customer has asked for it, no contract requires it, no date is
  attached to it, and nobody on the team knows what its API looks like.
- Twelve months of support tickets contain no request that relates to payment processors.
- Sizing from the team: the proposed scope is about two weeks; calling the processor's SDK
  directly from a single billing module is about three days.
- The registry, config-schema system, dynamic loader, and conformance suite would be permanent
  code that every future contributor to billing has to read.
