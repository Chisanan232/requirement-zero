# DEFER CLEANUP — the second report builder

**Artifact:** `analytics/report_builder_v2.py`, 900 lines. Appears to overlap
`analytics/report_builder.py`. Nothing in the repository calls it.

## Mission

Show customers what happened in their account, accurately.

## Objective the artifact serves

Unclear, which is the finding. It builds report structures, like the original builder does, but the
two produce different shapes and no code chooses between them.

## Origin

`git log --diff-filter=A -- analytics/report_builder_v2.py` finds a commit whose message is "wip
new report builder" with no ticket reference. The author no longer works on the project. There is no
PR description, no design note, and no linked issue. Subsequent commits are two dependency-driven
formatting passes and nothing else.

## Evidence

- `rg 'report_builder_v2|ReportBuilderV2'` — the module, and nothing else. No imports, no registry
  entry, no test.
- `rg 'report_builder_v2'` across config, CI, and deployment manifests — nothing.
- `git log -S'ReportBuilderV2'` — added in the one commit, never referenced from anywhere else in
  the entire history. No caller was ever written and then deleted.
- The analytics package is imported by name in one place using a config-driven module path
  (`getattr(module, config['builder'])`). The config value is currently the original builder. **The
  mechanism admits a value this repository cannot enumerate**, because the config is supplied per
  deployment.
- No test covers it, so nothing pins its behaviour either way.

## Confidence

**Low**, and specifically low in a way that blocks deletion rather than justifying it. Two things are
unresolved:

1. What the artifact was *for*. Without the original requirement, there is no way to know whether it
   represents abandoned work or an in-flight migration that stalled.
2. Whether any deployment's config selects it. The dynamic lookup means the code search cannot
   answer this; only the deployed config values can.

## Blast radius

Unknown, which is the point. If a deployment's config selects it, deleting the module breaks
report generation for that deployment at import time — a hard failure, not a degradation. If no
deployment selects it, the radius is a single unreferenced file and deletion is trivial.

The two possibilities differ by more than an order of magnitude in cost, and the evidence does not
distinguish them.

## Benefit and cost

Benefit if removed: 900 lines nobody reads, and one less thing to make an engineer ask "which
builder is the real one?" That is a genuine but small benefit.

Cost of being wrong: broken report generation in an unknown number of deployments, discovered at
startup.

## Verdict: DEFER CLEANUP

**Missing evidence, named:**

- The config value of `analytics.builder` in every deployed environment. One query or one look at
  the deployment configuration answers it.
- Whether anyone remembers the migration this was the start of. One question to the analytics
  owner.

**Trigger:** when both are answered. If no environment selects it and no migration is in flight, the
verdict becomes a high-confidence DELETE and the removal is a ten-minute change. If a migration *is*
in flight, the verdict becomes a decision about finishing or abandoning it, which is a product
question and not a cleanup.

## Retained

All of it, for now. It costs nothing to keep for another week; it costs an incident to remove on a
guess.

## Verification needed

None yet — nothing changes. The next action is the two questions above, not a diff.

## Why this is the honest verdict

The temptation is to call this DELETE. Everything visible in the repository supports it: no
references, no tests, no history, an absent author, a "wip" commit message. But "I could not find a
caller" and "there is no caller" are different claims, and the config-driven lookup is exactly the
mechanism that makes them different. Deferring costs one question. Guessing costs an outage in
someone else's environment.
