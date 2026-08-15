# CONSOLIDATE — three HTTP clients for one internal API

**Artifact:** `clients/billing_http.py`, `integrations/billing_client.py`, and the inline
`requests` calls in `jobs/invoice_sync.py`. All three talk to the same internal billing API.

## Mission

Bill customers the correct amount, on time.

## Objective the artifacts serve

Call the billing API: fetch invoices, post adjustments, read payment status. The behaviour is
required. Three implementations of it are not.

## Origin

`git log --diff-filter=A` on each: the first was written for the original invoice screen; the
second was added eight months later by a different team who did not find the first; the inline calls
in the sync job predate both and were never migrated. No commit message argues for having three —
each one was written as if it were the first.

## Evidence

- `rg 'billing_http|BillingHttpClient'` — 14 call sites, all in the web layer.
- `rg 'integrations.billing_client|BillingClient'` — 6 call sites, all in the admin tooling.
- `rg -n 'requests\.(get|post)' jobs/invoice_sync.py` — 4 direct calls with a hand-built URL.
- All three read the same base URL environment variable.
- **They are not equivalent.** `billing_http` retries on 5xx with backoff; `billing_client` does not
  retry at all; the inline calls in the sync job have no timeout set. Only `billing_http` handles
  the API's documented 409-on-duplicate-adjustment response.

## Confidence

High on the duplication; medium on the merge being behaviour-preserving. The divergence is the
finding: the three clients have different failure behaviour, so merging them *changes* two of the
three call paths.

## Blast radius

Crossing. Twenty-four call sites across the web layer, admin tooling, and a background job. The
sync job's missing timeout means consolidation gives it one for the first time — an improvement, but
a behaviour change: a call that previously hung forever will now raise.

## Benefit and cost

One client to reason about, and the 409 handling and retry policy reach the paths that currently
lack them. That last part is a latent correctness win: the sync job posts adjustments, and posting a
duplicate adjustment against a billing API is exactly the mistake that produces a wrong invoice.

Cost is a real migration across 24 call sites, plus tests for the two paths whose failure behaviour
changes.

## Verdict: CONSOLIDATE

**Survivor:** `billing_http`. It has the retry policy and the 409 handling, so the other two are
strictly less correct against the same API.

## Retained

Every call currently made, with the same request semantics. The retry and duplicate-handling
behaviour is added to the paths that lacked it, deliberately and named as a change rather than
smuggled in as a cleanup.

## Verification needed

Tests for the sync job's adjustment posting against a stubbed 409 and a stubbed timeout, written
*before* the migration so the new behaviour is pinned. Then the billing test modules and the
project's required gates. Migrate one caller group per commit — web, then admin, then the job — so a
revert is per-group.

## Note on ordering

Do not simplify `billing_client` or the inline calls first. They are being deleted; polishing them
is work done twice. Consolidate, then simplify the survivor if it needs it.
