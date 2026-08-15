---
id: 01-legacy-csv-export-path
expected_verdict: DELETE
case_type: obsolete-subsystem-should-be-deleted
example: ../../../skills/codebase-zero/examples/delete-legacy-csv-exporter.md
---

## The artifact

`reporting/legacy_csv.py`, containing a `LegacyCsvWriter` class, reachable only through the query
parameter `?format=csv_v1` on the report download route.

## What the system is for

A reporting product. Finance teams pull numbers out of it into their own spreadsheets and tools.

## Facts available

- The module was added in the commit that shipped the v2 report redesign. That commit's message says
  the old column layout is kept "for two release cycles" and links a ticket, now closed, that says
  the same thing.
- Two release cycles ended eleven months ago.
- A release note in the repository announced a removal date for the old layout. That date has passed.
- `rg 'csv_v1'` returns three hits: the route's parameter validation, the writer, and one test
  asserting the writer's header row.
- `rg 'LegacyCsvWriter'` returns the class, that same test, and nothing else. There is no registry,
  no factory map, and no dynamic lookup anywhere in the reporting package — the query parameter is
  validated against a hardcoded list of accepted values.
- Access logs for the reporting service are already collected and retained for 90 days. Zero requests
  in that window carried `format=csv_v1`.
- The writer formats rows on the fly. It stores nothing, and no other service imports the module.
