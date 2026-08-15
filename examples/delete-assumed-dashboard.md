---
id: delete-assumed-dashboard
verdict: DELETE
domain: internal tooling / observability
---

# DELETE — pipeline health dashboard

## Request

"Build a pipeline health dashboard: per-connector run status, throughput charts, 90-day
success-rate history, per-tenant drilldown."

## Provenance

Filed by an engineering manager as a post-mortem action item after a customer-visible ingest
outage. The stated authority is the action item itself: "the post-mortem says build visibility
into ingest." Nobody re-examined the action item after it was written at 1am during the incident
review.

## Fundamental objective

Not visibility. When a connector stalls, the on-call operator must learn within minutes and know
which connector and which tenant. A dashboard only meets that objective if a human is looking at
it, and nobody is looking at anything at 03:00.

## Evidence

- **Present evidence:** four operators total. Two comparable internal dashboards already exist;
  access logs show a median of three views per week each, and every view spike follows a page
  that had already told the operator there was an incident. Zero recorded cases of a problem being
  discovered by browsing a dashboard.
- **Imagined future:** a larger operations team that watches screens, and a future need for
  capacity trend analysis. Neither is staffed or requested.
- **If nothing is built:** nothing new breaks. The outage was not caused by missing charts. The
  actual gap is that "connector enabled but zero rows committed for 30 minutes" had no alert rule,
  so the stall ran for four hours before a customer reported it.

## Verdict

**DELETE.** The requirement does not earn its existence. It encodes an assumed solution
(a dashboard) rather than the validated need (the operator is told). The real gap is one alert
rule on a metric that is already emitted.

## Scope deleted

- Web UI, routing, and auth for a new operator surface
- Charting and throughput visualisation
- 90-day rollup tables and their retention/backfill jobs
- Per-tenant drilldown and its access-control model
- On-call runbook rewrite and training for a new tool

## Scope retained

- One alert rule on the existing `rows_committed` metric: enabled connector, zero rows, 30
  minutes, routed to the existing on-call rotation
- One runbook paragraph linked from the alert

## Next action

Write the stall alert. Return to the post-mortem author and rewrite the action item as "on-call is
paged within 30 minutes of a connector stall" so the next reader inherits the objective instead of
the assumed solution.
