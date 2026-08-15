# Blast Radius and Verification

Load this when a verdict is heading toward a change and you need to size what that change reaches
and what would catch a mistake.

Blast radius is not the diff size. It is the set of behaviors that can break, including behaviors
belonging to people who never see the diff.

## Enumerating what a change reaches

Work outward. Stop at the first ring you cannot enumerate, and say that you stopped there.

1. **The artifact itself** — its own behavior, and anything it privately owns.
2. **In-repo callers** — direct references, and callers of those callers where the behavior
   propagates rather than being absorbed.
3. **Tests and fixtures** — including tests that pass *because* of it without naming it. A test
   that mysteriously breaks is the radius telling you it was larger than you thought.
4. **Configuration and deployment** — flags, environment variables, manifests, secrets, schedules.
   Removing code while leaving a set flag behind produces silent divergence between environments.
5. **Persistent state** — data written in a format only this code can read, migrations already
   applied, queue messages already in flight, cache entries with a live TTL. Code is deployable;
   data already written is not.
6. **Out-of-repo consumers** — other services, client applications, SDK users, scripts operators
   run by hand, published API paths, documented import surfaces.

Rings 5 and 6 are the ones that turn a clean audit into an incident. If either is non-empty and
cannot be enumerated, the verdict is not high-confidence DELETE, regardless of how clean the code
search was.

## Sizing it

Three sizes, and the size determines what verification is required.

- **Contained** — the artifact and in-repo callers, all enumerated, all covered by tests. A revert
  is a single commit and restores the previous behavior exactly.
- **Crossing** — reaches configuration, deployment, another team's code, or a public surface. A
  revert restores the code but may not restore behavior, because something outside the repo has
  already adapted.
- **Irreversible** — touches data already written, a migration already applied, a message already
  published, or a contract already announced as removed. A revert does not undo it.

For an irreversible radius, deletion is not an engineering decision to make alone. Name the owner
and what they need to approve.

## Asymmetry of removal cost

The two errors are not equal, and pretending they are is how a cleanup becomes an outage.

- Keeping something unnecessary costs maintenance: reading it, building it, testing it, carrying it
  through refactors. It is continuous, visible, and bounded.
- Removing something necessary costs an incident: possibly data loss, a compliance gap, or a broken
  customer integration. It is discontinuous, and sometimes it does not surface for months.

So high-confidence removals should be quick and cheerful, and low-confidence removals should not
happen at all — DEFER CLEANUP is the correct verdict far more often than it feels like. The
resolution is never to hedge a verdict into vagueness; it is to state confidence accurately and act
according to it.

## Choosing verification that would actually catch the mistake

For each finding, name the check that would fail if the removal were wrong. Then ask whether that
check exists.

| Radius | Verification that is sufficient |
|---|---|
| Contained, well tested | The tests covering the behavior, then the project's required gates |
| Contained, untested | Write a test for the retained behavior first, then remove. If writing that test is impossible because nothing observes the behavior, that itself is the deletion argument — say so |
| Crossing config or deployment | Remove the code and the config together, and grep every environment definition. Verify no environment still sets what no longer exists |
| Crossing a public surface | A deprecation window with an announcement, not a removal. The verdict is DEFER CLEANUP until the window ends |
| Touching persistent state | A read path that tolerates both shapes, deployed and observed before the writer changes. Two changes, in order, never one |
| Irreversible | Owner approval and a written rollback plan, or do not proceed |

"Run the full test suite" is a real answer only after you have confirmed the suite covers this
artifact. A green suite that never exercised the deleted path proves the path was untested, not that
it was unused.

## Verifying the removal itself

After applying a finding:

- Review the effective diff against the base branch, not the last edit. Rebases and follow-up fixes
  hide scope creep.
- Check that nothing was removed beyond the finding. Incidental tidying inside a deletion PR makes
  the revert unusable, which is the one property the PR needed.
- Check that what the finding said would be retained is still retained, by naming it and finding it.
- If the tests needed changing to pass, stop and re-read the change. A test that had to be edited to
  accommodate a deletion was probably asserting the behavior you just removed.

## When the radius cannot be established

Say so, and downgrade. An audit that reports "blast radius unknown, therefore DELETE" has inverted
the burden of proof. Unknown radius means the finding is not ready: name the specific search,
owner, or observation that would establish it, and leave the artifact in place.
