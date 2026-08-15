# Gathering Evidence

Load this when you have an artifact in hand and need to establish what actually depends on it.

The verdict rests on this step. A confident DELETE on top of one `rg` call is not an audit; it is a
guess with formatting.

## Time-box, then commit

Search until the next search would not change the verdict, then stop. Practically: for each
artifact, look for current references, then tests, then history. If those three agree, you are
done. If they disagree, that disagreement *is* the finding — say so and set confidence low rather
than picking the reading you prefer.

Do not read the whole repository to audit one module. Do not ask the human anything you can
determine from the code.

## Searches that establish current use

Start broad on the name, then narrow. What matters is finding the reference you did not expect, so
search for the *string* as well as the symbol.

- **Symbol and text references** — `rg -n '\bSymbolName\b'`, then again without word boundaries,
  and once case-insensitively. Names get concatenated into other identifiers, embedded in log
  messages, and spelled in prose.
- **Dynamic reference** — the one grep misses. Search for the name as a plain string in
  registries, dispatch tables, factory maps, plugin manifests, `getattr`/reflection calls,
  serialized fixtures, and database rows. If the language has an entry-point or plugin mechanism,
  check its manifest.
- **Imports and the dependency direction** — who imports it, and does it import anything that only
  exists for it? An artifact with no importers but its own private helpers is a subtree, not a
  file: enumerate the whole subtree before sizing the removal.
- **Language tooling** — the type checker or LSP find-references is stronger than `rg` where it
  works, and worth one call. It is not stronger for dynamic dispatch, templates, or config.
- **Configuration and environment** — search the flag or variable name across config files,
  `.env` samples, CI definitions, deployment manifests, Helm/Terraform, and secret templates. A
  flag with no code reference but a live value in a deployment manifest is still telling you
  something is set in production.
- **Build and packaging** — is it named in the package manifest, an entry point, an export map, a
  public `__init__`, or a documented import path? A published export is a contract with callers
  you cannot enumerate.

## Searches that establish history

History answers "why", which decides between DELETE and DEFER CLEANUP.

- `git log --oneline -- <path>` — the change record and its recency.
- `git log --diff-filter=A -- <path>` — the commit that introduced it. Read its message and any
  linked ticket. This is the fastest route to the original requirement.
- `git log -S'SymbolName'` — where the symbol was added and removed across the whole history,
  including callers that no longer exist. Callers that were *deleted* are strong support for
  obsolescence; callers that were *renamed* are not.
- `git blame` on the load-bearing lines — who last touched it, and as part of what.
- `git log --oneline -- <path> | head -1` against the ticket tracker or PR references — where
  accessible, the linked discussion often states the requirement outright.

What history cannot tell you: whether something is used in production. A file can be untouched for
five years because it is correct. Recency is an input, never a verdict.

## Evidence by artifact type

| Artifact | What settles it |
|---|---|
| Function, class, module | References, dynamic lookups, tests, exported surface |
| Abstraction, interface, factory, registry | How many implementations exist *today*, and whether any second consumer is committed with a date |
| Compatibility or legacy layer | Who the old callers are, whether they can be enumerated, and whether a deprecation window was ever announced and ended |
| Dependency | Import sites; whether stdlib or an existing dependency now covers it; transitive cost |
| Feature flag | Current value in every environment, the last time it flipped, and whether both branches still work |
| Config or environment variable | Read sites in code, and set sites in manifests and CI |
| API endpoint or schema field | Server-side route registration, client code in this repo, published docs, and access logs where already collected |
| Background job, worker, queue | The producer, the consumer, the schedule definition, and whether anything reads the output |
| Cache | Whether a hit-rate or latency number was ever measured; an unmeasured cache is unproven, not proven useless |
| Database table or migration | Read and write sites, and whether the migration has run everywhere — an applied migration is history and cannot be edited |
| CI workflow | What decision its result gates; a check nobody blocks on is a notification |
| Test or fixture | What behavior it pins, and whether that behavior still exists |
| Documentation | Whether it describes current behavior; documentation for removed behavior is worse than none |

## Setting confidence honestly

Three levels, and the honest majority of first-pass findings are medium.

- **High** — you enumerated the dependents and there is a closed set of them. Static language,
  private symbol, references found and counted, tests cover the behavior.
- **Medium** — searches came back clean but the mechanism admits references you cannot see:
  dynamic dispatch, a published export, config-driven behavior, an external client.
- **Low** — the artifact's purpose is not established, evidence conflicts, or the only support for
  removal is that nothing recent touched it.

Always state the single thing that would raise the confidence. "High if a search of the client
repositories finds no callers" is actionable; "further investigation needed" is not.

Never write "no dependencies found" when you mean "I did not look". Say which searches you ran.

## Evidence you should not manufacture

- Do not add telemetry, logging, or instrumentation in order to justify a cleanup. That is a
  larger project than the cleanup, and it is a new requirement in its own right.
- Do not treat an absent test as evidence the behavior is unimportant. Untested and unimportant are
  different claims, and the gap between them is where outages live.
- Do not infer usage from plausibility. If you cannot find a caller and cannot rule one out, that
  is DEFER CLEANUP with the missing evidence named.
