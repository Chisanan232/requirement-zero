---
id: 04-csv-import-error-report
expected_verdict: BUILD
case_type: straightforward-implementation-is-correct
example: ../../examples/build-csv-import-recovery.md
---

## Requirement as filed

"Our CSV importer rejects the whole file on the first bad row. Give users a row-level error
report so they can fix the rows and re-upload."

The same thread offers three possible additions: an in-browser CSV editor so users can fix rows
in place, automatic correction with fuzzy column mapping, and an import history page with a
re-run button.

## Who filed it, and on what authority

Filed by the support team. The filing cites specific support tickets by number.

## Facts available

- 41 support tickets in 90 days, all the same shape: "import failed, I don't know why." Most come
  from existing customers re-importing updated rosters; the rest come from trials.
- Median time from signup to first successful import is 3.5 days. Six of the 19 trials last
  quarter never completed an import at all.
- Support resolves each ticket by asking for the file, running a local script over it, and mailing
  back the offending line numbers. Roughly 40 minutes each.
- The importer already parses and validates rows one at a time before committing anything; it
  raises on the first parse or validation failure and discards the rest of the file.
- Every customer who reported this maintains the source data in a spreadsheet.
- No ticket has ever asked to re-run a previous import, and none has asked to edit data inside the
  product.
