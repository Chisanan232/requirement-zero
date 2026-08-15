# DELETE — the legacy CSV export path

**Artifact:** `reporting/legacy_csv.py` plus its `LegacyCsvWriter` class and the `?format=csv_v1`
query parameter that reaches it.

## Mission

Give finance teams numbers they can trust, exportable into their own tools.

## Objective the artifact served

Let a customer download a report in the column layout the product used before the v2 report
redesign, so that spreadsheets built against the old layout kept working through the transition.

## Origin

`git log --diff-filter=A -- reporting/legacy_csv.py` lands on a commit whose message names the v2
redesign and a ticket promising the old layout "for two release cycles". The linked ticket is
closed. Two release cycles ended eleven months ago, and a release note in the repository announced
the removal date, which has passed.

## Evidence

- `rg 'csv_v1'` — three hits: the route's parameter validation, the writer itself, and one test
  asserting the writer's header row.
- `rg 'LegacyCsvWriter'` — the class, its test, and nothing else. No registry entry, no dynamic
  lookup, no factory map.
- Access logs, already collected for the reporting service, show zero requests carrying
  `format=csv_v1` in the retained 90-day window.
- The deprecation was announced in-product and in the release notes, with a date that has passed.

## Confidence

High. The parameter is the only entry point, it is enumerable in the route definition, the
announcement window closed, and the log evidence is direct rather than inferred.

## Blast radius

Contained. The route's validation, the writer, its test. Nothing persists in the old layout — the
writer formats on the fly and stores nothing. No other service imports the module.

## Benefit and cost

Removes a second export path that every column change has had to be applied to twice, and one
branch in the route. Cost is one small deletion and the removal of a test that asserts the layout
being removed.

## Verdict: DELETE

The original requirement was explicitly time-boxed, the box closed, the deprecation was announced,
and no traffic arrived during the window. This is the case where deletion is cheerful and quick.

## Retained

The v2 export path, unchanged. Nothing about the current layout depends on the old one.

## Verification needed

Confirm the removed parameter value now returns the route's standard validation error rather than a
500. Run the reporting test module. Grep the deployment manifests once for `csv_v1` in case a
scheduled export job pins it — the code search covered the repository, and a manifest is not code.

## What would have made this KEEP instead

Any of: a deprecation window still open; one enterprise customer's scheduled job still calling it;
the layout persisted somewhere; or callers outside this repository that could not be enumerated. In
those cases the answer is DEFER CLEANUP with the trigger named, not DELETE.
