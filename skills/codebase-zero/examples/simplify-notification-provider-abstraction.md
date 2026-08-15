# SIMPLIFY — the notification provider abstraction

**Artifact:** `notifications/` — the `NotificationProvider` abstract base class, the
`ProviderRegistry`, the `providers.yaml` configuration file, the `PROVIDER_BACKEND` environment
variable, and the single concrete implementation `SendgridProvider`.

## Mission

Users find out about things that happened in their account.

## Objective the artifact serves

Send transactional email. That is required and nobody is questioning it.

## Origin

`git log --diff-filter=A -- notifications/registry.py` finds a commit whose message says "so we can
swap providers later". The linked ticket describes a possible migration away from the email vendor
that has not been proposed since. No second provider was ever written.

## Evidence

- `rg 'NotificationProvider'` — the base class, the one subclass, the registry, and a test that
  instantiates the subclass through the registry.
- `rg 'ProviderRegistry|register_provider'` — the registry, one registration call at import time,
  and the same test.
- `providers.yaml` contains exactly one entry, `sendgrid`.
- `rg 'PROVIDER_BACKEND'` across code, CI, and deployment manifests — read in one place, set to
  `sendgrid` in every environment, never set to anything else in the file's history
  (`git log -S'PROVIDER_BACKEND'`).
- No second provider exists, and no ticket or PR proposes one with a date.

## Confidence

High that the indirection is unused. The registry is internal, private to the package, and not part
of any published surface — the set of consumers is closed and small.

## Blast radius

Contained. Four files inside `notifications/`, one import-time registration, one config file, one
environment variable that must come out of the deployment manifests in the same change as the code.

## Benefit and cost

Removes a base class, a registry, a YAML file, an environment variable, and a layer of indirection
between "send this email" and the code that sends it. Every future change to notification behaviour
currently has to be threaded through an abstract interface that has exactly one implementation.

Cost is small: inline the concrete class, delete the registry and the config, remove the variable
from every manifest.

## Verdict: SIMPLIFY

The behaviour — sending email — is entirely justified. The structure around it was built for a second
provider that has never been committed to. One implementation of an interface is a concrete thing
wearing a costume.

## Retained

Sending email through the current vendor, with identical behaviour: same call sites, same templates,
same failure handling. Nothing user-visible changes.

## Verification needed

The notification tests, rewritten to call the concrete class directly. Confirm no environment
still sets `PROVIDER_BACKEND` after the change, in every manifest and CI definition — leaving a set
variable behind for code that no longer reads it is how environments silently diverge.

## Why not DELETE, and why not KEEP

DELETE is wrong: the emails are needed. KEEP would be right if a second provider were committed with
a date, or if the registry were a published extension point with callers outside this repository.
Neither holds. A second provider arriving later costs one afternoon to reintroduce, against carrying
the indirection through every change until then.
