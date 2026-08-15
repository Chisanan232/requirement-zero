---
id: 06-orphaned-report-builder
expected_verdict: DEFER CLEANUP
case_type: insufficient-evidence-blocks-removal
example: ../../../skills/codebase-zero/examples/defer-cleanup-report-builder.md
---

## The artifact

`analytics/report_builder_v2.py`, 900 lines. It builds report structures, overlapping in purpose with
`analytics/report_builder.py`, though the two produce different output shapes.

## What the system is for

An analytics product. It shows customers what happened in their account, accurately.

## Facts available

- `rg 'report_builder_v2|ReportBuilderV2'` finds the module and nothing else. No imports, no
  registration, no test.
- `rg 'report_builder_v2'` across config files, CI definitions, and deployment manifests in this
  repository: nothing.
- `git log -S'ReportBuilderV2'` shows it was added in one commit and never referenced from anywhere
  else at any point in history. No caller was ever written and later deleted.
- That commit's message is "wip new report builder". It has no ticket reference, no PR description,
  and no linked design note. Its author no longer works on the project.
- Later commits touching the file are two dependency-driven formatting passes.
- The analytics package selects its builder through a dynamic lookup:
  `getattr(module, config['builder'])`. The `config['builder']` value is supplied per deployment, not
  committed to this repository.
- In the one configuration file present in the repository, `builder` is set to the original builder.
- Nobody has yet been asked about the module, and the deployed configuration values have not been
  checked.
