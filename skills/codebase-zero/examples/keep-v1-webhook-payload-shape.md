# KEEP — the v1 webhook payload shape

**Artifact:** `webhooks/v1_payload.py` — the code that emits the flat, snake_case webhook payload,
alongside the current nested v2 payload. Untouched for three years apart from dependency-driven
formatting commits.

## Mission

Let customers automate their own workflows off events in the product.

## Objective the artifact serves

Deliver events to customer HTTP endpoints in the payload shape those endpoints were written against.

## Origin

`git log --diff-filter=A` finds the original webhook implementation. When v2 was added, the commit
adding it explicitly kept v1: subscriptions record a `payload_version`, and existing subscriptions
stayed on v1. No deprecation was ever announced.

## Evidence

- `rg 'v1_payload|payload_version'` — the emitter, the subscription model, one branch in the
  delivery worker, and its tests.
- **The database has the answer the code does not.** Subscriptions with `payload_version = 1` still
  exist and are active. The number is not zero.
- Public API documentation, in this repository, documents the v1 payload shape as a supported
  format.
- No deprecation notice was ever sent, and no removal date exists anywhere.
- Three years of no changes: the file's history shows only formatting and dependency commits.

## Confidence

High, and notably the confidence is high *for keeping*, which is a real verdict and not a failure to
decide. The evidence directly contradicts the removal hypothesis: live subscriptions, documented
support, no deprecation.

## Blast radius

Irreversible if removed. Customer-side code that this repository cannot see would begin receiving a
shape it does not parse. The failure appears in the customer's system, not in any dashboard here,
and it appears as data quietly not arriving. A revert restores the emitter but does not undo the
events already delivered in the wrong shape or the automations that failed in between.

## Benefit and cost

Removing it buys one branch in the delivery worker and one module. That is the entire benefit.
Against it: broken customer integrations, no way to notify affected parties after the fact, and a
support incident whose cost is measured in accounts.

## Verdict: KEEP

Three years without a change is not evidence of abandonment. It is what a finished, stable
compatibility contract looks like. The artifact is doing exactly what it was kept for.

## Retained

All of it, unchanged.

## Verification needed

None — nothing changes. If the maintainers *want* this gone, the work is not a deletion, it is a
deprecation project: announce a removal date, notify the accounts on `payload_version = 1`, give
them a migration window, then delete after the window closes. That is a product decision with a
named owner, not a cleanup.

## The trap in this case

Every heuristic a code-minimization pass uses points at deletion: old, untouched, duplicated by a
newer implementation, low complexity score, no recent authors. The only evidence that saves it is
outside the code — live rows in a table and a documented public contract. An audit that reasons from
the repository's shape alone deletes this artifact and finds out from a customer.
