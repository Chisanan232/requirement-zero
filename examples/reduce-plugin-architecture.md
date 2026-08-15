---
id: reduce-plugin-architecture
verdict: REDUCE
domain: platform architecture
---

# REDUCE — payment provider plugin architecture

## Request

"Before we add Stripe billing, build a payment provider plugin architecture: a `PaymentProvider`
interface, a provider registry, per-provider config schemas, dynamic loading from
`providers/*.py`, and a conformance test suite every provider must pass."

## Provenance

Proposed by the implementing engineer, endorsed in review as "architecture requires we not couple
to a vendor." Traced back: no architecture document says this. The phrase originates from a
principle page about avoiding vendor lock-in, which does not mandate a plugin system. The second
provider is named in a sales deck as a possibility for enterprise customers in EMEA; no customer
has asked, and no contract requires it.

## Fundamental objective

Take payment from customers today, and be able to add a second processor later without a rewrite
we cannot afford. The second half is real; the question is what it actually costs to keep.

## Evidence

- **Present evidence:** one processor (Stripe), one currency, one checkout flow. Charge, refund,
  and webhook reconciliation are the only operations the product uses.
- **Imagined future:** an EMEA processor for local payment methods. Plausible, unscheduled,
  unvalidated. Nobody knows what its API shape is, so the interface would be designed against a
  single implementation and would almost certainly be wrong for the second one.
- **If nothing extra is built:** the billing code calls Stripe directly. Adding a second processor
  later means extracting an interface from *two known* implementations — the situation in which
  the interface can actually be designed correctly.
- **Cost of the imagined future is not zero:** dynamic loading, registry, config schemas, and a
  conformance suite are permanent surface that every future contributor must understand, and they
  make the one real provider harder to debug.

## Verdict

**REDUCE.** The need to avoid a rewrite is real. The proposed scope is a generalisation built from
one example, which is the condition under which abstractions are most often wrong. Keep the seam,
delete the framework.

## Scope deleted

- Provider registry and dynamic loading from `providers/*.py`
- Per-provider config schema system
- Conformance test suite with no second implementation to conform
- `PaymentProvider` abstract interface generalised from a single case

## Scope retained

- One concrete `StripePayments` module with three functions: `charge`, `refund`,
  `reconcile_webhook`
- Callers depend on that module rather than on Stripe's SDK directly, so the call sites are already
  the seam
- No abstraction beyond the module boundary

## Next action

Ship `StripePayments`. Note in the billing module that the interface should be extracted when a
second processor is contracted — not before, because the second implementation is what reveals the
correct shape.

## Note

Technical elegance is not the tiebreaker here. A plugin architecture is a more interesting thing
to build and a better line on a design doc than three functions, and neither of those facts is
user value. The user experiences a successful charge identically in both designs.
