---
id: 03-notification-provider-abstraction
expected_verdict: SIMPLIFY
case_type: single-implementation-indirection-should-collapse
example: ../../../skills/codebase-zero/examples/simplify-notification-provider-abstraction.md
---

## The artifact

The `notifications/` package: an abstract base class `NotificationProvider`, a `ProviderRegistry`
that maps names to classes at import time, a `providers.yaml` file, an environment variable
`PROVIDER_BACKEND` selecting the entry, and one concrete class `SendgridProvider` that sends the
email.

## What the system is for

A SaaS application. Users need to find out about things that happened in their account, and
transactional email is how they find out.

## Facts available

- `rg 'NotificationProvider'` finds the base class, one subclass, the registry, and a test that
  instantiates the subclass through the registry.
- `rg 'ProviderRegistry|register_provider'` finds the registry, one registration call at import
  time, and that same test.
- `providers.yaml` contains exactly one entry: `sendgrid`.
- `rg 'PROVIDER_BACKEND'` across code, CI definitions, and deployment manifests: read in one place,
  set to `sendgrid` in every environment. `git log -S'PROVIDER_BACKEND'` shows it has never been set
  to any other value in the file's history.
- The commit that added the registry says "so we can swap providers later" and links a ticket
  describing a possible migration away from the current email vendor. That migration has not been
  proposed again since. No second provider class was ever written.
- The registry is private to the `notifications` package. It is not exported, not documented, and not
  part of any published API surface.
- The emails themselves are sent constantly and are load-bearing: password resets go through this
  path.
