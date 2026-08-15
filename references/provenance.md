# Requirement Provenance

Load this when a requirement's justification is a role, a document, a norm, or a phrase rather
than a person, an event, or a number.

Provenance is the chain from a requirement back to the thing in the world that forces it. A
requirement with no chain is a preference someone wrote confidently. The job here is not to
disbelieve the requester — it is to find the actual constraint, because the constraint determines
the scope, and a misread constraint produces work nobody needed.

## Resolving an authority claim

Every claim below is unresolved provenance. Ask the question; conclude from the answer.

### "Legal says we need this" / "for compliance" / "for the audit"

Ask: which regulation, contract clause, policy, or audit finding, and what exactly does it
require? Who signed off on this interpretation?

- Names a clause, standard, or finding → the clause is the requirement. Scope to the clause and
  nothing further. Frequently narrower than the request: a retention rule says how long to keep
  records, not that you need a records-management UI.
- Names a person in legal or compliance who reviewed it → treat as a protective constraint,
  default retain, and scope the implementation rather than the obligation.
- Cannot name either → do not delete it and do not build the full request. Build nothing yet;
  escalate to get the obligation identified. An unread obligation is the most expensive kind to
  guess at, in both directions.

### "Architecture requires it" / "it's our standard" / "the platform team said so"

Ask: which decision record or standard, and what problem was it adopted to prevent? Does that
problem apply to this case?

- Documented decision whose problem applies here → BUILD, scoped to that problem.
- Documented decision whose problem does not apply → REDUCE or DELETE, and say which condition
  is absent. Standards accumulate cases they were never meant for.
- No record, only convention → treat as no evidence. Consistency alone does not justify scope.

### "Industry best practice" / "everyone does it this way"

Ask: what failure does the practice prevent, and have we seen that failure or measured its risk?

- A specific failure that plausibly applies → the failure is the requirement. Ask what the
  cheapest thing that prevents it is; often much smaller than the practice.
- No specific failure → DELETE. This phrase carries no information about your system.

### "The CEO / a customer / the client asked for it"

Ask: what were they trying to accomplish when they asked? What told them they needed this?

- An outcome emerges → the outcome is the requirement, and the requested artifact is one
  candidate solution among several. Solve the outcome; report that you did so and why.
- A named customer with a contract or renewal at stake → that is evidence. Weight it, and still
  run DELETE on the parts.
- Nobody can reconstruct the intent → DEFER, with the trigger being the requester restating what
  they need. Do not build a guess at an executive's mental model.

### "Users have been asking for it"

Ask: how many, who, when, and in what words? Where is that recorded?

- Named requests with quotes → evidence. Read the words rather than the summary; the summary is
  usually a solution the requester invented, not their problem.
- Aggregate feeling with no record → treat as one anecdote, not a trend. DEFER.

### "It's already in the spec / the ticket / the roadmap"

Ask: who wrote it, and what did they know at the time? Has anything changed since?

A requirement's presence in a document is not provenance — documents inherit unvalidated scope
and then launder it into authority through age. Trace it to the original reason or treat it as
unsupported.

## Handling silence

If provenance cannot be established because nobody is available to ask:

- Speculative scope → DEFER, and record the question you could not get answered.
- Protective constraint → retain, and record that it is retained on the basis of unverified
  provenance so a reviewer can see the open question. Any proposal to weaken it still needs the
  owner's decision and the applicable security, legal, or compliance review — unreachable
  provenance is not a substitute for that review.

Never convert "I could not find the reason" into "there is no reason." Write down which one it
is. The distinction is the difference between a challenged requirement and a guess.

## Recording what you found

State provenance in one line in the evidence section: source type, who or what, and date if
known. For example: "production incident INC-4412, 2026-03, checkout timeouts at p99" or
"unresolved: 'legal requires 7-year retention', no clause identified, owner not reachable."
The second line is a useful artifact. A vague summary is not.
