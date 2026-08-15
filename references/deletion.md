# Deletion Rules

Load this when running step 2 (DELETE) on a requirement with multiple parts, or when deciding
whether a specific piece of scope survives.

Deletion is attempted before simplification because simplifying unnecessary work is wasted work.
The unit of deletion is not the feature — it is every part of it, examined separately.

## The test

For the requirement, then for each part: **if this ships without it, who notices, and through
what signal?**

Both answers must be concrete. "Users" is not an observer; "the checkout team's on-call, via the
failed-payment alert" is. "It would be worse" is not a signal; "the p99 exceeds the 400ms SLO in
the load test" is.

| Observer named | Signal named | Verdict for that part |
|---|---|---|
| yes | yes | Retain |
| yes | no | Ask for the signal once; unanswered → DELETE |
| no | yes | Retain only if the signal is an automated protection (alert, constraint, test) |
| no | no | DELETE |

If nothing in the whole requirement survives, the verdict is DELETE. If the core survives and
parts do not, the verdict is REDUCE and the deleted parts are the list.

## What to enumerate as parts

Run the test against each of these, not just the headline feature:

- Fields on a model or payload, and states in a state machine
- Options, flags, settings, environment variables, feature toggles
- Endpoints, routes, methods, CLI subcommands, event types
- Layers of indirection: interfaces, base classes, factories, adapters, wrappers, registries
- New dependencies, services, queues, caches, and datastores
- Steps in a process: approvals, handoffs, reviews, sign-offs, status transitions
- Screens, tabs, modals, and empty states
- Migration and backfill work, and the code that keeps both paths alive
- Documents and reports produced but not read

## Rules that decide specific cases

The "Deletion that is out of scope" list below **overrides every rule in this section**. If a
rule here would delete something on that list, the list wins and the answer is to scope the
implementation rather than remove the protection.

- **One implementation, no committed second consumer** → delete the abstraction, keep the
  concrete implementation. "Committed" means a named consumer with a date. An interface with a
  single implementer is a naming convention with extra steps.
- **Configurability nobody requested** → delete the setting, hardcode the value. Cost of change
  later is one edit; cost of carrying it is every code path, test, and doc that branches on it.
- **A flag whose off state is never used in production** → delete the flag and the dead branch.
  Not a kill switch or a degradation path: those exist unused by design, and the day they are
  needed is the day nobody has time to rebuild one.
- **Symmetry or completeness arguments** ("we support CSV, so we should support XML") → delete
  unless the new case has its own observer and signal. Symmetry is an aesthetic, not a user.
- **Defensive code for a state the type system or a database constraint already prevents** →
  delete. Defensive code for a state that has actually occurred → retain, with a test. This rule
  stops at trust boundaries: a type declaration is a compile-time claim, not a runtime check, so
  validation of anything deserialized from outside the process — request bodies, webhooks, file
  uploads, queue messages, third-party responses — is input validation and is not deletable here.
- **A cache with no measured latency or cost problem** → delete. Add it when there is a number.
- **A queue or async path where the synchronous version meets the SLO** → delete.
- **A generic solution for one case** → delete the generality, solve the case. The second case
  will teach you more about the right abstraction than the prediction will.
- **An admin or internal tool that duplicates a database query someone runs monthly** → delete;
  the query is the tool until frequency or audience changes.
- **A metric, log, or dashboard with no consumer and no alert attached** → delete. Observability
  that nobody reads is cost, not insight. Audit and security logs are the exception: they are
  read retrospectively, after an incident or on request, so "no current consumer" is their normal
  state and not evidence against them.
- **Backward compatibility for a caller you can enumerate and update** → delete the compatibility
  layer, update the callers. For a *published* interface with unknown callers, this is a
  protective constraint: retain.
- **A process step whose output has never changed a decision** → delete the step.

## Deletion that is out of scope

Do not delete on your own authority:

- Security controls, authentication, authorization, encryption, input validation, audit trails
- Safety interlocks, rate limits, circuit breakers, and kill switches — whether or not an incident
  has already happened. A control with a clean record may be working, not idle.
- Data integrity constraints, and privacy and data-retention behavior, consent flows, deletion
  rights
- Regulatory or contractual obligations
- Compatibility of an interface with callers you cannot enumerate

For these, the challenge is aimed at the *size of the implementation*, not the existence of the
protection. Ask what the smallest thing is that keeps the guarantee intact, and route any
proposal that weakens the guarantee to the owner and the appropriate reviewer. Record the
residual risk in writing. Absence of evidence about a threat is not evidence that the protection
is unnecessary — that inference is backwards precisely where it is most expensive.

## Deleting existing code as the answer

Before proposing new work, check whether the outcome is reachable by removing something. A
requirement to "make the import flow clearer" is often satisfied by deleting two of its five
options. This is the highest-value BUILD available and it is easy to miss, because the request
was phrased as an addition.

## Failure modes when deleting

- **Deleting the outcome instead of the scope.** If the smaller version no longer produces the
  observable outcome, it is not simpler — it is a different, unrequested requirement.
- **Deleting to hit a size target.** There is no line, file, or dependency count to reach.
- **Deleting the hard part because it is hard.** If the difficulty is where the value lives, the
  verdict is BUILD HARD. See `mission-alignment.md`.
- **Bundling the deletion into the implementation silently.** State the deleted scope explicitly
  so the human can object to it.
