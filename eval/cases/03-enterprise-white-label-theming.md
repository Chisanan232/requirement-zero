---
id: 03-enterprise-white-label-theming
expected_verdict: DEFER
case_type: deferral-is-correct
example: ../../examples/defer-enterprise-white-label.md
---

## Requirement as filed

"Add per-tenant white-labelling: custom logo, colour palette, custom email sender domain, and
customer-supplied CSS overrides on the hosted app."

## Who filed it, and on what authority

"The CEO asked for it after a prospect call." Traced: on a discovery call the prospect asked
whether white-labelling was *possible*. The deal is not at contract stage. Asked directly, the
CEO's stated position is "don't lose the deal over it."

## Facts available

- Zero tenants are entitled to white-labelling today. There are zero contractual commitments to
  it, and no signed agreement mentions branding.
- Twelve months of support tickets searched for "logo", "branding", and "white label" return one
  hit: the same prospect's question, logged by the account executive.
- Tenant config already stores a display name. Reading a logo URL and a primary colour from it
  instead of from hardcoded constants is a small, self-contained change.
- Customer-supplied CSS would be written against the app's internal class names. The team has no
  versioned public class-name surface and changes markup freely between releases.
- Custom email sender domains need per-tenant DNS verification, SPF/DKIM setup, and deliverability
  monitoring. Nobody has scoped that work.
- Enterprise branding is a common pattern in this market segment; two competitors offer it.
- On previous enterprise deals, sales has answered capability questions with "available on the
  enterprise plan, on request" and the deals proceeded.
