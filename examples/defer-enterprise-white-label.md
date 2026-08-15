---
id: defer-enterprise-white-label
verdict: DEFER
domain: product / multi-tenancy
---

# DEFER — white-label theming for enterprise tenants

## Request

"Add per-tenant white-labelling: custom logo, colour palette, custom email sender domain, and
customer-supplied CSS overrides on the hosted app."

## Provenance

"The CEO asked for it after a prospect call." Traced: the prospect asked whether white-labelling
was *possible*, during discovery, and the deal is not in contract stage. The CEO's actual position
on being asked directly is "don't lose the deal over it" — not "build it now." No other tenant has
raised it in twelve months of support tickets.

## Fundamental objective

Do not lose enterprise deals for want of a branding story. That objective can be met by a credible
answer as well as by shipped code, and today it has no committed consumer or delivery date.

## Evidence

- **Present evidence:** zero tenants entitled to it, zero contractual commitments, one
  exploratory question. Support ticket search for "logo", "branding", "white label": one hit, the
  same prospect.
- **Imagined future:** an enterprise tier where branding is table stakes. Plausible — this is a
  real pattern in the market — but the *shape* is unknown. Customer-supplied CSS in particular is a
  decision that is very hard to reverse: once a tenant ships CSS against internal class names, every
  future UI change is a breaking change for them.
- **If nothing is built:** the sales answer becomes "on the enterprise plan, on request" and the
  deal proceeds. Nothing in the product breaks.
- **Cost of building now:** the design would be guessed. Guessing wrong on the CSS override
  surface creates permanent compatibility obligations to a tenant who does not yet exist.

## Verdict

**DEFER.** Plausible value, insufficient present evidence, and an expensive-to-reverse design
decision that a real customer would specify for us. Not DELETE — the need is credible and
market-standard, and deleting it would lose real information. Not BUILD — there is no consumer.

## Scope deleted

Nothing is deleted. This scope is parked with a written trigger, not discarded; DEFER without a
trigger is just DELETE with extra steps.

## Scope retained

- The requirement, recorded with its trigger and its known-unknowns (CSS override surface,
  email-domain verification path)
- Cheap, non-committing preparation only where it costs nothing today: logo and primary colour
  read from existing tenant config rather than being hardcoded

## Trigger to revisit

Either of:

1. A signed contract or written commitment naming white-labelling as a requirement, or
2. Two additional tenants requesting it independently.

On trigger, re-run Requirement Zero on the *then*-known requirement — likely reducing it to logo
and palette, and explicitly re-deciding customer-supplied CSS rather than inheriting it.

## Next action

Give sales the "enterprise plan, on request" answer. Record the trigger. Build nothing.
