---
id: 01-pipeline-health-dashboard
expected_verdict: DELETE
case_type: building-nothing-is-correct
example: ../../examples/delete-assumed-dashboard.md
---

## Requirement as filed

"Build a pipeline health dashboard: per-connector run status, throughput charts, 90-day
success-rate history, per-tenant drilldown."

## Who filed it, and on what authority

Filed by an engineering manager as a post-mortem action item after a customer-visible data
ingest outage. The authority claimed is the action item itself: "the post-mortem says build
visibility into ingest." The action item was written at 1am during the incident review and has
not been looked at since.

## Facts available

- The operations team is four engineers. There is no operations centre and no screen anyone
  watches. Out of hours, one on-call engineer carries a pager.
- Two comparable internal dashboards already exist. Their access logs show a median of three
  views per week each. Every spike in views follows a page. There is no recorded case of a
  problem first being noticed by someone browsing a dashboard.
- The outage: one connector stayed enabled but committed zero rows for four hours. A customer
  reported it. The pipeline emits a per-connector `rows_committed` metric continuously, and that
  metric recorded the stall correctly at the time.
- Existing alert rules cover process crashes, API error rates, and queue depth. Alerts route to
  the on-call rotation and page within a minute.
- The action item also mentions a larger operations team that would watch screens, and future
  capacity trend analysis. Neither is staffed, scheduled, or requested by anyone.
- Rough sizing from the team: three to four weeks for one engineer, covering a new
  operator-facing web surface with its own routing and auth, charting, 90-day rollup tables with
  retention and backfill jobs, and a per-tenant access-control model.
