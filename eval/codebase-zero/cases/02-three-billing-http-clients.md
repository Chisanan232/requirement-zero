---
id: 02-three-billing-http-clients
expected_verdict: CONSOLIDATE
case_type: duplicate-implementations-should-become-one
example: ../../../skills/codebase-zero/examples/consolidate-three-http-clients.md
---

## The artifact

Three ways of calling the same internal billing API:

- `clients/billing_http.py`, exposing `BillingHttpClient`
- `integrations/billing_client.py`, exposing `BillingClient`
- direct `requests.get` / `requests.post` calls with a hand-built URL inside
  `jobs/invoice_sync.py`

## What the system is for

A subscription product. It bills customers the correct amount, on time.

## Facts available

- `rg 'billing_http|BillingHttpClient'` finds 14 call sites, all in the web layer.
- `rg 'integrations.billing_client|BillingClient'` finds 6 call sites, all in the admin tooling.
- `rg -n 'requests\.(get|post)' jobs/invoice_sync.py` finds 4 direct calls.
- All three read the same base URL from the same environment variable, and all three are pointed at
  the same API.
- Their behaviour differs. `BillingHttpClient` retries on 5xx with backoff and handles the API's
  documented 409 response for a duplicate adjustment. `BillingClient` does neither. The inline calls
  in the sync job do neither and set no timeout.
- `jobs/invoice_sync.py` posts adjustments, which is the endpoint that returns 409 on a duplicate.
- Git history: `BillingHttpClient` was added for the invoice screen. `BillingClient` was added eight
  months later by a different team. The inline calls predate both. No commit message anywhere argues
  for having more than one.
- The web layer, the admin tooling, and the sync job are all in this repository. No external service
  imports any of the three.
