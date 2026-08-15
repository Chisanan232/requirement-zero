# Worked Audits

Seven audits, one per verdict plus a protective-constraint case. Each shows the artifact, the mission
it is judged against, the evidence actually gathered, the verdict, and the seven fields a verdict
must carry.

The details are constructed, not drawn from a real repository. What they demonstrate is the shape of
the reasoning and, in several cases, the specific way a plausible-looking removal is wrong.

| Audit | Verdict | What it demonstrates |
|---|---|---|
| [Legacy CSV exporter](delete-legacy-csv-exporter.md) | DELETE | A time-boxed requirement whose box closed: announced deprecation, passed date, zero traffic, enumerable entry point |
| [Three HTTP clients](consolidate-three-http-clients.md) | CONSOLIDATE | Duplicates that quietly diverged, so merging them changes behaviour — and naming which one survives |
| [Notification provider abstraction](simplify-notification-provider-abstraction.md) | SIMPLIFY | One implementation behind a base class, registry, config file, and environment variable |
| [v1 webhook payload](keep-v1-webhook-payload-shape.md) | KEEP | Three years untouched and still a live contract; the saving evidence is outside the code |
| [Order matching engine](invest-matching-engine.md) | INVEST | The highest-cost, highest-churn, most-feared subsystem is where to spend more, not less |
| [Second report builder](defer-cleanup-report-builder.md) | DEFER CLEANUP | "I found no caller" is not "there is no caller" when the lookup is config-driven |
| [Payment idempotency guard](keep-idempotency-replay-guard.md) | KEEP | A protective mechanism whose quiet counter is evidence it works, not evidence it is idle |

If you read two, read [the v1 webhook case](keep-v1-webhook-payload-shape.md) and
[the matching engine](invest-matching-engine.md). Both are artifacts that every maintenance-cost
heuristic ranks first for removal, and both would be expensive mistakes — which is the difference
between this audit and a cleanup pass.
