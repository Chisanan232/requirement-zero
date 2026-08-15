---
id: build-csv-import-recovery
verdict: BUILD
domain: product / onboarding
---

# BUILD — row-level error report for CSV import

## Request

"Our CSV importer rejects the whole file on the first bad row. Give users a row-level error report
so they can fix and re-upload."

## Provenance

Filed by support, backed by named tickets rather than an abstract principle. No appeal to authority
was needed or made.

## Fundamental objective

A new customer gets their existing data into the product without a support engineer doing it for
them. Import is the first thing every customer does; failing it silently loses the customer before
they see any value.

## Evidence

- **Present evidence:** 41 support tickets in 90 days, all the same shape: "import failed, I don't
  know why." Median time-to-first-successful-import is 3.5 days, and 6 of 19 trials in the last
  quarter never completed an import at all. Support currently fixes these by asking for the file,
  running a local script, and mailing back the offending line numbers — roughly 40 minutes each.
- **Imagined future scale:** not needed. The evidence is entirely from current behaviour with
  current customers.
- **If nothing is built:** onboarding keeps failing, support keeps hand-running scripts, and trial
  conversion keeps leaking at the first step. This is the rare case where the answer to "what
  breaks if we do nothing?" is "something already visibly broken stays broken."

## Verdict

**BUILD.** Necessary, aligned to the objective, evidenced by current users. Build the smallest
version that removes the failure — which is not the same as the largest version anyone suggested.

## Scope deleted

The request arrived with adjacent suggestions that did not survive QUESTION and FOCUS:

- In-browser CSV editor to fix rows in place (solves a different job; the user's spreadsheet is
  already a better editor than anything we would build)
- Auto-correction and fuzzy column mapping (guessing at customer data; a wrong guess is worse than
  a clear error)
- Import history page with re-run (no evidence anyone wants to re-run an old import)

## Scope retained

- Import validates all rows and continues past failures instead of aborting on the first
- Valid rows commit; invalid rows are collected
- One downloadable errors CSV: original row number, the offending column, and a plain-language
  reason
- The summary shown after upload: N imported, M failed, download the report

## Next action

Implement all-rows validation and the errors CSV. Instrument time-to-first-successful-import so the
next decision about import has evidence instead of intuition.
