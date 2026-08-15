# KEEP — the payment idempotency replay guard

**Artifact:** `payments/idempotency.py` — a table of request keys with a 24-hour retention window,
checked before every charge is submitted to the processor. It adds a database round-trip to the
charge path.

## Mission

Charge customers the correct amount, exactly once.

## Objective the artifact serves

Stop a retried charge request from producing a second charge. The client retries on timeout; without
the key check, a timeout that actually succeeded upstream becomes a double charge.

## Origin

`git log --diff-filter=A -- payments/idempotency.py` finds a commit referencing an incident ticket.
The ticket is closed and its description is one line: "duplicate charges, see incident channel". The
incident channel is not in this repository. Nobody currently on the team was present.

## Evidence

- `rg 'idempotency_key'` — the guard, the charge path, the client SDK that generates the key, and
  the processor request builder.
- The key-store table has rows. It is written on every charge.
- **Nothing has read a duplicate in fourteen months.** The guard's "already seen this key" branch has
  a counter, and the counter has not incremented in the retained metrics window.
- The latency cost is real and measured: one database round-trip on the charge path, which the filed
  cleanup request quantifies correctly.
- No regulation or contract clause naming idempotency was found in the repository. The original
  incident's details are not recoverable from what is here.

## Confidence

High for KEEP. Note what that confidence rests on: not on finding a justifying document, but on
recognizing what kind of artifact this is and what its evidence profile is supposed to look like.

## The inversion this case turns on

A quiet counter is the *expected* reading for a working guard. Client retries are rare; a guard that
catches nothing during a calm fourteen months is a guard doing its job on the days that are not
calm. Reading "no duplicates detected" as "duplicates cannot happen" reverses cause and effect —
the mechanism is part of why the number is zero.

The same reading applied to a kill switch, a circuit breaker, or an audit log produces the same
error. Absence of an incident is not evidence the protection is unnecessary, and that inference is
backwards precisely where it is most expensive.

## Blast radius

Irreversible. Removing the guard does not fail loudly; it fails on the next timeout-and-retry, as a
customer charged twice. The consequence is money moved incorrectly, discovered by the customer, plus
a chargeback and a trust cost. A revert restores the code and does not un-charge the card.

## Benefit and cost

Benefit: one database round-trip removed from the charge path — a real latency improvement, honestly
measured by the person who filed the request.

Cost: the failure mode the guard exists to prevent, in a payment system, where "exactly once" is the
mission statement.

## Verdict: KEEP

Not because a document was found justifying it, but because it is a protective mechanism on the
mission-critical path, and no evidence was produced that duplicate submission has become impossible.
The burden of proof sits on removal, and it was not met.

## What is legitimately in scope

The *implementation* can be challenged; the protection cannot. Worth auditing separately:

- Is the 24-hour retention window right, or would a shorter one cover every real retry pattern? A
  measurement of observed retry intervals would answer it, and a smaller table is cheaper to query.
- Is the round-trip on the hot path avoidable — a conditional insert rather than a read-then-write,
  or a check colocated with the charge record's own write?
- Is the key store's index doing what a query plan would show?

Each of those is a genuine SIMPLIFY candidate on the implementation, with the protection intact.
That is the shape of a correct answer here: challenge the size, not the existence.

## What would change the verdict

A named owner deciding to accept the risk, with the residual risk written down, and the client's
retry behaviour changed so that a retry cannot reach the processor twice. That is a payments
decision with an owner, not a latency cleanup — and it would still not be a decision for an audit
to make on its own authority.
