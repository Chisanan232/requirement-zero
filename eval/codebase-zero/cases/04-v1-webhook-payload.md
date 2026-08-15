---
id: 04-v1-webhook-payload
expected_verdict: KEEP
case_type: old-looking-code-is-a-live-contract
example: ../../../skills/codebase-zero/examples/keep-v1-webhook-payload-shape.md
guard: compatibility-contract-not-deleted
---

## The artifact

`webhooks/v1_payload.py`, which emits a flat snake_case webhook payload. A newer nested payload
lives alongside it in `webhooks/v2_payload.py`. The delivery worker branches between them on a
`payload_version` column on the subscription record.

## The request that prompted this audit

An engineer doing a cleanup pass flagged it: "This file hasn't been touched in three years, it's
duplicated by v2, and it's got the worst maintainability score in the package. Nobody has touched it
since before I joined. Can we drop it and simplify the delivery worker down to one path?"

## What the system is for

A B2B product. Customers automate their own workflows off events in the product, and webhooks are
how the events reach them.

## Facts available

- `rg 'v1_payload|payload_version'` finds the emitter, the subscription model, one branch in the
  delivery worker, and their tests.
- The file's git history over three years contains only formatting changes and dependency-driven
  commits. No behavioural change.
- The commit that added v2 explicitly kept v1: it introduced the `payload_version` column and left
  existing subscriptions on version 1.
- Subscription records with `payload_version = 1` still exist in the database and are active. The
  count is not zero.
- The public API documentation in this repository documents the v1 payload shape as a supported
  format.
- No deprecation notice for v1 was ever sent to customers, and no removal date exists anywhere in the
  repository or the tracker.
- The receiving endpoints belong to customers. This repository contains none of their code.
