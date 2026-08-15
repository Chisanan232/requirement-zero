#!/usr/bin/env python3
"""Compare agent verdicts on the same cases with and without one of this repository's skills.

Two arms, identical user prompts. The only difference is that the `skill` arm gets the skill's
SKILL.md body appended to the system prompt. Standard library only; shells out to the `claude` CLI.

Two profiles, selected with `--profile`, each with its own skill, case corpus, verdict vocabulary,
and prompt: `requirement-zero` (the default) and `codebase-zero`.

Runs are isolated with `--safe-mode` (no ambient CLAUDE.md discovery from the working directory)
and `--tools ""` (tools removed from the model's schema). Both matter for validity: see
eval/README.md "Isolation".

    python3 eval/run_eval.py                              # requirement-zero: 6 cases x 2 arms x 3 runs
    python3 eval/run_eval.py --profile codebase-zero      # the codebase-zero corpus
    python3 eval/run_eval.py --runs 1 --case 01           # one cheap pair of calls
    python3 eval/run_eval.py --self-test                  # verdict-extraction checks, no calls
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
RESULTS_DIR = EVAL_DIR / "results"

UNPARSEABLE = "UNPARSEABLE"  # model answered, but no readable VERDICT line: a real non-match
ERRORED = "ERRORED"          # CLI/harness failure: excluded from match-rate denominators
CALL_TIMEOUT_S = 300

# Claude Code truncates a skill listing entry's combined `description` and `when_to_use` at this
# many characters (host default; raisable via `skillListingMaxDescChars`). Over it, the entry is
# shortened rather than rejected -- which keeps the skill's name and can drop the exclusions at the
# end of the description. Neither skill here uses `when_to_use`, so this is the description budget.
DESCRIPTION_CAP = 1536

# Both arms receive this identical prompt, including the verdict vocabulary and an explicit
# licence to build nothing. That makes the baseline deliberately strong; see eval/README.md.
PROMPT_TEMPLATE = """You are an engineer deciding what to do about an incoming requirement.

Read the requirement and the situational facts below and decide what should actually be built,
if anything.

Reach exactly one verdict from this vocabulary:

- DELETE - build nothing; the requirement does not deserve to exist.
- REDUCE - the underlying need is real, but the proposed scope is larger than the need.
- DEFER - value is plausible but nothing is blocked today; revisit on a named trigger.
- BUILD - build it, at the smallest size that meets the need.
- BUILD HARD - it is genuinely hard and expensive, and it must stay hard, because the
  difficulty is where the value lives.

Building nothing, or building far less than was asked for, is an acceptable and often correct
answer. So is building the hard and expensive thing in full. Commit to one verdict; do not hedge
and do not offer the user a menu.

Report briefly, in this order:

1. Fundamental objective - the observable outcome required.
2. Evidence and its provenance.
3. Scope you are NOT building, itemised.
4. Scope you ARE building, itemised.
5. The single next action.

End your response with a final line in exactly this form, with nothing after it:

VERDICT: <one of DELETE, REDUCE, DEFER, BUILD, BUILD HARD>

--- INCOMING REQUIREMENT ---

{body}
"""

# Floor check only: did the response name what it is not building at all? Both arms are asked for
# that section explicitly, so expect this at ceiling in both. It is deliberately phrasing-agnostic
# ("scope NOT building" / "scope NOT being built" / "deleted scope" all count) because an earlier,
# narrower pattern measured wording differences between the arms rather than behaviour.
DELETED_SCOPE_RE = re.compile(
    r"(scope\s+(you\s+are\s+)?(not|deleted)\b|not\s+(being\s+)?(built|building)|deleted scope|dropping|removed from scope)",
    re.IGNORECASE,
)

# The codebase-zero corpus audits code that already exists, so the decision, the vocabulary, and
# the report differ. Same structure as above: both arms get this identical prompt, it names the
# whole vocabulary, and it explicitly licenses the answers that are not deletion.
CODEBASE_PROMPT_TEMPLATE = """You are an engineer auditing an artifact that already exists in a
codebase, deciding whether it still deserves to exist.

Read the artifact description and the situational facts below and decide what should actually
happen to it, if anything.

Reach exactly one verdict from this vocabulary:

- DELETE - it no longer earns its existence; remove it.
- CONSOLIDATE - several artifacts do the same job; the behaviour stays and one implementation
  survives.
- SIMPLIFY - the behaviour is justified but the implementation carries structure nothing uses.
- DEFER CLEANUP - it looks removable, but the evidence or the risk does not justify acting now.
- KEEP - it still earns its place as it is.
- INVEST - it is complex and expensive and it is where the mission is currently won or lost;
  spend more engineering here rather than simplifying the capability away.

Removing nothing is an acceptable and often correct answer, and so is concluding that an expensive
subsystem deserves more investment rather than less. Commit to one verdict; do not hedge and do not
offer the user a menu.

Report briefly, in this order:

1. Fundamental objective - the outcome this artifact serves.
2. Evidence, and what it does not establish.
3. Confidence, and what would raise it.
4. Blast radius if it changed.
5. What is retained.
6. Verification needed.

End your response with a final line in exactly this form, with nothing after it:

VERDICT: <one of DELETE, CONSOLIDATE, SIMPLIFY, DEFER CLEANUP, KEEP, INVEST>

--- ARTIFACT UNDER AUDIT ---

{body}
"""

# One profile per skill. Verdict tuples are matched in the order written, so any verdict that is a
# prefix of a later one must come first -- "DEFER CLEANUP" after "DEFER" would be a silent misread.
# _assert_prefix_safe below enforces that at import rather than trusting this comment.
# false_rejections are the verdicts that are wrong for this corpus's must-not-lose-it cases: for
# requirement-zero, refusing work that should be built; for codebase-zero, removing or downgrading
# something the case establishes as load-bearing.
PROFILES: dict[str, dict[str, object]] = {
    "requirement-zero": {
        "skill_path": REPO_ROOT / "SKILL.md",
        "cases_dir": EVAL_DIR / "cases",
        "prompt": PROMPT_TEMPLATE,
        "verdicts": ("BUILD HARD", "DELETE", "REDUCE", "DEFER", "BUILD"),
        "protective_verdicts": ("BUILD", "BUILD HARD"),
        "false_rejections": ("DELETE", "DEFER"),
        "required_description_terms": ("safety", "security", "legal", "compliance"),
    },
    "codebase-zero": {
        "skill_path": REPO_ROOT / "skills" / "codebase-zero" / "SKILL.md",
        "cases_dir": EVAL_DIR / "codebase-zero" / "cases",
        "prompt": CODEBASE_PROMPT_TEMPLATE,
        "verdicts": ("DEFER CLEANUP", "DELETE", "CONSOLIDATE", "SIMPLIFY", "KEEP", "INVEST"),
        "protective_verdicts": ("KEEP", "INVEST"),
        "false_rejections": ("DELETE", "CONSOLIDATE", "SIMPLIFY"),
        # The carve-back categories. Each must survive in the description, because the
        # already-decided exclusion routes past the audit and only these words pull it back.
        "required_description_terms": (
            "security", "safety", "privacy", "data-integrity", "legal", "compliance",
            "compatibility", "requirement-zero",
        ),
    },
}


def _assert_prefix_safe() -> None:
    """Fail at import if any profile's vocabulary can misread one verdict as another.

    Matching walks the tuple in order, so a verdict that is a prefix of a later member (DEFER
    before DEFER CLEANUP, BUILD before BUILD HARD) would return the short one and silently corrupt
    every metric downstream. Checked here because the ordering is hand-written per profile and a
    comment asking for it is not a guarantee.
    """
    for name, profile in PROFILES.items():
        verdicts: tuple[str, ...] = profile["verdicts"]  # type: ignore[assignment]
        for i, short in enumerate(verdicts):
            for long in verdicts[i + 1:]:
                if long.startswith(short):
                    raise SystemExit(
                        f"profile {name!r}: {long!r} can never match because {short!r} precedes it; "
                        f"list the longer verdict first."
                    )


def _assert_scoring_sets_sane() -> None:
    """Fail at import if a profile's scoring sets cannot produce a meaningful safety number.

    `false_rejections` is the metric this suite leads with, and nothing else validates it: an empty
    tuple or a typo'd member yields 0 false rejections on every run, which is indistinguishable from
    the correct answer and is exactly the published value. Same for `protective_verdicts`, which
    `load_cases` only exercises through case frontmatter. Both must be non-empty, both must name
    verdicts this profile can actually return, and they must not overlap -- a verdict cannot be both
    the answer that loses load-bearing scope and the answer that preserves it.

    `required_description_terms` is checked here for the same reason, because the check it feeds has
    the same vacuous-pass shape: an empty list satisfies every term and prints the success line.
    """
    for name, profile in PROFILES.items():
        verdicts: tuple[str, ...] = profile["verdicts"]  # type: ignore[assignment]
        sets = {
            "protective_verdicts": profile["protective_verdicts"],
            "false_rejections": profile["false_rejections"],
        }
        for key, members in sets.items():
            if not members:
                raise SystemExit(f"profile {name!r}: {key} is empty; every run would score 0.")
            unknown = sorted(set(members) - set(verdicts))  # type: ignore[arg-type]
            if unknown:
                raise SystemExit(
                    f"profile {name!r}: {key} names {unknown}, which this profile can never "
                    f"return; such a member scores nothing. Vocabulary is {list(verdicts)}."
                )
        overlap = sorted(set(sets["protective_verdicts"]) & set(sets["false_rejections"]))
        if overlap:
            raise SystemExit(
                f"profile {name!r}: {overlap} is listed as both protective and a false rejection."
            )
        # Same reasoning one level up: an empty term list makes check_descriptions() pass
        # vacuously and print the same success line as a real pass, and a missing key makes it
        # die on a KeyError instead of saying what is wrong.
        if not profile.get("required_description_terms"):
            raise SystemExit(
                f"profile {name!r}: required_description_terms is missing or empty; the "
                f"description check would pass without checking anything."
            )


_assert_prefix_safe()
_assert_scoring_sets_sane()


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split a `---` delimited `key: value` frontmatter block from the body. No YAML needed."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("case file has no frontmatter")
    meta: dict[str, str] = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[i + 1 :]).strip()
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    raise ValueError("unterminated frontmatter")


def load_cases(profile: dict[str, object], case_filter: str | None) -> list[dict[str, object]]:
    cases_dir: Path = profile["cases_dir"]  # type: ignore[assignment]
    verdicts: tuple[str, ...] = profile["verdicts"]  # type: ignore[assignment]
    protective: tuple[str, ...] = profile["protective_verdicts"]  # type: ignore[assignment]
    cases = []
    for path in sorted(cases_dir.glob("*.md")):
        if case_filter and not path.name.startswith(case_filter):
            continue
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        missing = {"id", "expected_verdict", "case_type", "example"} - meta.keys()
        if missing:
            raise ValueError(f"{path.name}: missing frontmatter keys {sorted(missing)}")
        if meta["expected_verdict"] not in verdicts:
            raise ValueError(f"{path.name}: bad expected_verdict {meta['expected_verdict']!r}")
        if not (path.parent / meta["example"]).resolve().is_file():
            raise ValueError(f"{path.name}: example path does not resolve: {meta['example']}")
        # A guard fails when the arm reaches a scope-losing verdict on something the case
        # establishes as load-bearing, so a guard on a case that expects a scope-losing verdict can
        # never fail. Rejecting it here is the difference between an armed guard and a decorative
        # one that inflates guard_scored_runs while guard_failures stays structurally at zero.
        if meta.get("guard") and meta["expected_verdict"] not in protective:
            raise ValueError(
                f"{path.name}: declares guard {meta['guard']!r} but expects "
                f"{meta['expected_verdict']!r}, which is not one of {protective}. Such a guard can "
                f"never fail."
            )
        cases.append({"file": path.name, "meta": meta, "body": body})
    if not cases:
        raise SystemExit(f"no cases matched {case_filter!r} under {cases_dir}")
    return cases


def skill_body(profile: dict[str, object]) -> str:
    """The shipped skill, read from disk at run time so the eval always tests what ships."""
    skill_path: Path = profile["skill_path"]  # type: ignore[assignment]
    _, body = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
    if not body.strip():
        raise SystemExit(  # otherwise both arms silently become identical and report a null result
            f"{skill_path.name} has an empty body: the skill arm would be identical to baseline."
        )
    return body


# Verdict tails seen in practice carry Markdown emphasis, backticks, quote markers, non-breaking
# spaces, and hyphenated forms. Normalise all of that away before matching, or BUILD HARD gets
# silently misread as BUILD -- which corrupts the one metric everything else rests on.
_TAIL_STRIP = "*_`>#~\"'. \t "


def _normalise_tail(tail: str) -> str:
    for ch in (" ", "*", "`", "_", "-"):
        tail = tail.replace(ch, " ")
    return re.sub(r"\s+", " ", tail).strip().upper()


def extract_verdict(text: str, verdicts: tuple[str, ...]) -> str:
    """Read the final `VERDICT:` line. Never guess: anything else is UNPARSEABLE.

    `verdicts` is the active profile's vocabulary, and it is required. An earlier version defaulted
    it to the union of both profiles' verdicts, which made --self-test pass against a vocabulary no
    real run ever uses -- so the test could not detect a mis-ordered profile tuple, which is the one
    failure it exists to catch.
    """
    for line in reversed(text.strip().splitlines()):
        line = line.strip().strip(_TAIL_STRIP)
        if not line.upper().lstrip(_TAIL_STRIP).startswith("VERDICT"):
            continue
        tail = _normalise_tail(line.split(":", 1)[-1])
        for verdict in verdicts:  # in tuple order; _assert_prefix_safe guarantees no shadowing
            if tail.startswith(verdict):
                return verdict
        return UNPARSEABLE
    return UNPARSEABLE


# (profile, input, expected) triples for --self-test. Each case runs against that profile's real
# vocabulary -- the same tuple a real run uses -- so a mis-ordered tuple fails here rather than
# corrupting a paid run. Costs nothing and defends verdict extraction, which every metric rests on.
SELF_TEST_CASES = (
    ("requirement-zero", "VERDICT: BUILD HARD", "BUILD HARD"),
    ("requirement-zero", "VERDICT: BUILD **HARD**", "BUILD HARD"),
    ("requirement-zero", "VERDICT: BUILD  HARD", "BUILD HARD"),
    ("requirement-zero", "VERDICT: BUILD-HARD", "BUILD HARD"),
    ("requirement-zero", "VERDICT: BUILD_HARD", "BUILD HARD"),
    ("requirement-zero", "VERDICT: BUILD HARD", "BUILD HARD"),
    ("requirement-zero", "VERDICT: `BUILD HARD`", "BUILD HARD"),
    ("requirement-zero", "> VERDICT: BUILD HARD", "BUILD HARD"),
    ("requirement-zero", "**VERDICT: BUILD HARD**", "BUILD HARD"),
    ("requirement-zero", "prose\n\nVERDICT: BUILD HARD.", "BUILD HARD"),
    ("requirement-zero", "VERDICT: BUILD", "BUILD"),
    ("requirement-zero", "verdict: build", "BUILD"),
    ("requirement-zero", "**VERDICT: DELETE**", "DELETE"),
    ("requirement-zero", "VERDICT: `DEFER`", "DEFER"),
    ("requirement-zero", "VERDICT: REDUCE", "REDUCE"),
    ("requirement-zero", "VERDICT: maybe", UNPARSEABLE),
    ("requirement-zero", "no verdict line at all", UNPARSEABLE),
    ("requirement-zero", "", UNPARSEABLE),
    ("requirement-zero", "VERDICT: BUILD HARD\nVERDICT: DELETE", "DELETE"),  # last line wins
    # A verdict belonging only to the other profile is not guessed at, it is UNPARSEABLE.
    ("requirement-zero", "VERDICT: CONSOLIDATE", UNPARSEABLE),
    # codebase-zero vocabulary. DEFER CLEANUP must not degrade to DEFER, and the two-word forms
    # arrive with the same emphasis and hyphenation noise the five-verdict set already showed.
    ("codebase-zero", "VERDICT: DEFER CLEANUP", "DEFER CLEANUP"),
    ("codebase-zero", "VERDICT: DEFER-CLEANUP", "DEFER CLEANUP"),
    ("codebase-zero", "**VERDICT: DEFER CLEANUP**", "DEFER CLEANUP"),
    ("codebase-zero", "VERDICT: `DEFER  CLEANUP`.", "DEFER CLEANUP"),
    ("codebase-zero", "VERDICT: DEFER", UNPARSEABLE),  # bare DEFER is the other profile's verdict
    ("codebase-zero", "VERDICT: BUILD HARD", UNPARSEABLE),
    ("codebase-zero", "VERDICT: DELETE", "DELETE"),
    ("codebase-zero", "VERDICT: CONSOLIDATE", "CONSOLIDATE"),
    ("codebase-zero", "VERDICT: SIMPLIFY", "SIMPLIFY"),
    ("codebase-zero", "VERDICT: KEEP", "KEEP"),
    ("codebase-zero", "VERDICT: INVEST", "INVEST"),
    ("codebase-zero", "verdict: invest", "INVEST"),
)


def _parsed_description(skill_path: Path) -> str:
    """The `description` as the host sees it, with YAML's enclosing quotes removed if present."""
    meta, _ = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
    value = meta.get("description", "")
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
    return value


def check_descriptions() -> list[str]:
    """The `description` is the trigger surface, and nothing else in this repository checks it.

    It decides whether the skill is selected at all, so an exclusion dropped from it cannot be
    recovered by any rule in the body -- the body is never read. It is also the field most often
    edited and the one whose length was twice measured wrong. Three things are checked: it exists,
    it fits the host's per-entry listing cap, and it still names every term the profile declares
    load-bearing. A term silently dropped during an edit fails here rather than in production.
    """
    problems = []
    for name, profile in PROFILES.items():
        skill_path: Path = profile["skill_path"]  # type: ignore[assignment]
        required: tuple[str, ...] = profile["required_description_terms"]  # type: ignore[assignment]
        description = _parsed_description(skill_path)
        if not description:
            problems.append(f"[{name}] {skill_path.name} has no description; the skill cannot be "
                            f"selected on anything but its name.")
            continue
        if len(description) > DESCRIPTION_CAP:
            problems.append(f"[{name}] description is {len(description)} chars, over the "
                            f"{DESCRIPTION_CAP}-char listing cap; the entry would be truncated and "
                            f"the exclusions are at the end.")
        missing = [term for term in required if term not in description]
        if missing:
            problems.append(f"[{name}] description no longer names {missing}; each is a category "
                            f"the body treats as load-bearing, and the description is the only "
                            f"place that can keep the skill from being routed past it.")
    return problems


def self_test() -> int:
    failures = [
        (profile, raw, expected, got)
        for profile, raw, expected in SELF_TEST_CASES
        if (got := extract_verdict(raw, PROFILES[profile]["verdicts"])) != expected  # type: ignore[arg-type]
    ]
    for profile, raw, expected, got in failures:
        print(f"FAIL [{profile}] {raw!r}: expected {expected!r}, got {got!r}")
    print(f"{len(SELF_TEST_CASES) - len(failures)}/{len(SELF_TEST_CASES)} "
          f"verdict-extraction cases pass across {len(PROFILES)} profile vocabularies")
    description_problems = check_descriptions()
    for problem in description_problems:
        print(f"FAIL {problem}")
    print(f"{len(PROFILES) - len(description_problems)}/{len(PROFILES)} skill descriptions "
          f"present, within the {DESCRIPTION_CAP}-char listing cap, and naming their required terms")
    return 1 if failures or description_problems else 0


def call_claude(prompt: str, system_prompt: str | None) -> dict[str, object]:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", "sonnet",
        "--max-turns", "1",
        # --tools "" removes tools from the model's schema. --allowed-tools "" only withholds
        # permission, which leaves the tools visible and turns an attempted call into a failed run.
        "--tools", "",
        # --safe-mode stops CLAUDE.md discovery from CWD upward. Without it an ambient project
        # CLAUDE.md is injected into BOTH arms; see eval/README.md "Isolation".
        "--safe-mode",
    ]
    if system_prompt is not None:
        cmd += ["--append-system-prompt", system_prompt]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CALL_TIMEOUT_S)
    except (subprocess.TimeoutExpired, OSError) as exc:  # no retries: record and move on
        return {"error": f"{type(exc).__name__}: {exc}"}
    if proc.returncode != 0:
        return {"error": f"exit {proc.returncode}: {proc.stderr.strip()[:500]}"}
    try:
        return {"payload": json.loads(proc.stdout)}
    except json.JSONDecodeError as exc:
        return {"error": f"unparseable CLI JSON: {exc}"}


def run_once(
    case: dict[str, object], arm: str, skill: str, run_index: int, profile: dict[str, object]
) -> dict[str, object]:
    meta = case["meta"]  # type: ignore[index]
    expected = meta["expected_verdict"]
    record: dict[str, object] = {
        "case": case["file"], "arm": arm, "run": run_index, "expected_verdict": expected,
    }
    prompt_template: str = profile["prompt"]  # type: ignore[assignment]
    outcome = call_claude(
        prompt_template.format(body=case["body"]), skill if arm == "skill" else None
    )
    if "error" in outcome:
        record.update(error=outcome["error"], verdict=ERRORED, matched=False)
        return record

    payload: dict = outcome["payload"]  # type: ignore[assignment]
    text = payload.get("result") or ""
    usage = payload.get("usage") or {}
    model_usage = payload.get("modelUsage") or {}
    # A CLI-level failure (is_error, or a missing/empty result -- e.g. the turn was consumed by an
    # attempted tool call) is an ERRORED run, not a wrong answer. Scoring it as UNPARSEABLE would
    # silently charge the arm with a non-match for a harness/CLI problem.
    if payload.get("is_error") or not text.strip():
        record.update(
            error=f"CLI reported failure: subtype={payload.get('subtype')!r} "
                  f"is_error={payload.get('is_error')!r} result_empty={not text.strip()}",
            verdict=ERRORED, matched=False,
            input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"),
            cost_usd=payload.get("total_cost_usd"), duration_ms=payload.get("duration_ms"),
            model=",".join(sorted(model_usage)) or None, is_error=payload.get("is_error"),
            response_text=text,
        )
        return record
    verdict = extract_verdict(text, profile["verdicts"])  # type: ignore[arg-type]
    protective: tuple[str, ...] = profile["protective_verdicts"]  # type: ignore[assignment]
    false_rejections: tuple[str, ...] = profile["false_rejections"]  # type: ignore[assignment]
    record.update(
        # Only whitelisted fields are kept: no session ids, uuids, or local paths.
        verdict=verdict,
        matched=verdict == expected,
        false_rejection=expected in protective and verdict in false_rejections,
        named_deleted_scope=bool(DELETED_SCOPE_RE.search(text)),
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        cache_creation_input_tokens=usage.get("cache_creation_input_tokens"),
        cache_read_input_tokens=usage.get("cache_read_input_tokens"),
        cost_usd=payload.get("total_cost_usd"),
        duration_ms=payload.get("duration_ms"),
        model=",".join(sorted(model_usage)) or None,
        is_error=payload.get("is_error"),
        response_text=text,
    )
    return record


def majority(verdicts: list[str]) -> str:
    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    winners = sorted(v for v, c in counts.items() if c == top)
    return winners[0] if len(winners) == 1 else "TIE(" + "/".join(winners) + ")"


def summarise(records: list[dict[str, object]], cases: list[dict[str, object]], arms: list[str]) -> dict:
    per_case = []
    for case in cases:
        row: dict[str, object] = {
            "case": case["file"],
            "expected_verdict": case["meta"]["expected_verdict"],  # type: ignore[index]
            "guard": case["meta"].get("guard"),  # type: ignore[union-attr]
        }
        for arm in arms:
            runs = [r for r in records if r["case"] == case["file"] and r["arm"] == arm]
            scored = [r for r in runs if r["verdict"] != ERRORED]  # errored runs are not answers
            row[arm] = {
                "verdicts": [r["verdict"] for r in runs],
                "majority": majority([str(r["verdict"]) for r in scored]) if scored else None,
                "matches": sum(1 for r in scored if r["matched"]),
                "scored_runs": len(scored),
                "errored_runs": len(runs) - len(scored),
                "runs": len(runs),
                "mean_output_tokens": round(
                    sum(r.get("output_tokens") or 0 for r in scored) / len(scored), 1
                ) if scored else None,
            }
        per_case.append(row)

    # Guard cases declare themselves with a `guard:` frontmatter key. Selecting them by filename
    # prefix instead would silently stop guarding the moment a corpus numbers its cases differently.
    guard_cases = {c["file"] for c in cases if c["meta"].get("guard")}  # type: ignore[union-attr]

    totals = {}
    for arm in arms:
        runs = [r for r in records if r["arm"] == arm]
        scored = [r for r in runs if r["verdict"] != ERRORED]
        guard = [r for r in scored if r["case"] in guard_cases]
        matches = sum(1 for r in scored if r["matched"])
        totals[arm] = {
            "runs": len(runs),
            # Match rate is over SCORED runs only: an ERRORED run is a harness/CLI failure, not a
            # wrong answer, so it must not silently penalise the arm.
            "scored_runs": len(scored),
            "errored_runs": len(runs) - len(scored),
            "matches": matches,
            "match_rate": round(matches / len(scored), 3) if scored else None,
            "false_rejections": sum(1 for r in scored if r.get("false_rejection")),
            "unparseable": sum(1 for r in scored if r["verdict"] == UNPARSEABLE),
            "named_deleted_scope": sum(1 for r in scored if r.get("named_deleted_scope")),
            "guard_scored_runs": len(guard),
            "guard_failures": sum(1 for r in guard if r.get("false_rejection")),
            "total_output_tokens": sum(r.get("output_tokens") or 0 for r in scored),
            "total_cost_usd": round(sum(r.get("cost_usd") or 0.0 for r in runs), 4),
        }
    return {"per_case": per_case, "totals": totals}


def print_table(summary: dict, arms: list[str]) -> None:
    print("\nPer-case verdicts (expected -> per-run verdicts, majority)")
    for row in summary["per_case"]:
        print(f"\n  {row['case']}  expected={row['expected_verdict']}"
              + (f"  guard={row['guard']}" if row.get("guard") else ""))
        for arm in arms:
            a = row[arm]
            print(f"    {arm:<9} {', '.join(a['verdicts']) or '-':<40} majority={a['majority']}")
    print("\nAggregate  (match rate is over SCORED runs; ERRORED runs are excluded)")
    print(f"  {'arm':<9} {'match':<8} {'rate':<7} {'false-rej':<10} {'unparse':<8} {'errored':<8} "
          f"{'guard-fail':<11} {'out-tok':<8} {'cost$':<8}")
    for arm, t in summary["totals"].items():
        print(f"  {arm:<9} {str(t['matches']) + '/' + str(t['scored_runs']):<8} "
              f"{str(t['match_rate']):<7} {t['false_rejections']:<10} {t['unparseable']:<8} "
              f"{t['errored_runs']:<8} {t['guard_failures']:<11} "
              f"{t['total_output_tokens']:<8} {t['total_cost_usd']:<8}")
    for arm, t in summary["totals"].items():
        if t["errored_runs"]:
            print(f"\n  !!! {arm} arm had {t['errored_runs']} ERRORED run(s) excluded from the "
                  f"match rate. Investigate before quoting any number. !!!")
    for arm, t in summary["totals"].items():
        if t["guard_failures"]:
            print(f"\n  *** GUARD FAILED: {arm} arm reached a scope-losing verdict on a guard case "
                  f"{t['guard_failures']} of {t['guard_scored_runs']} scored run(s). ***")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(PROFILES), default="requirement-zero",
                        help="which skill and case corpus to evaluate (default requirement-zero)")
    parser.add_argument("--runs", type=int, default=3, help="runs per arm per case (default 3)")
    parser.add_argument("--case", help="only cases whose filename starts with this, e.g. 01")
    parser.add_argument("--arm", choices=("baseline", "skill"), help="only this arm")
    parser.add_argument("--self-test", action="store_true",
                        help="check verdict extraction against known tricky strings; makes no calls")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    profile = PROFILES[args.profile]
    cases = load_cases(profile, args.case)
    arms = [args.arm] if args.arm else ["baseline", "skill"]
    skill = skill_body(profile)
    total_calls = len(cases) * len(arms) * args.runs
    print(f"profile {args.profile}: {len(cases)} case(s) x {len(arms)} arm(s) x {args.runs} "
          f"run(s) = {total_calls} CLI calls")

    records: list[dict[str, object]] = []
    for run_index in range(1, args.runs + 1):
        for case in cases:
            for arm in arms:
                record = run_once(case, arm, skill, run_index, profile)
                records.append(record)
                print(f"  run {run_index} {case['file'][:2]} {arm:<9} -> {record['verdict']}"
                      + (f"  ERROR {record['error']}" if "error" in record else ""))
                sys.stdout.flush()

    summary = summarise(records, cases, arms)
    models = sorted({str(r.get("model")) for r in records if r.get("model")})
    model_slug = re.sub(r"[^A-Za-z0-9.-]+", "-", models[0]) if models else "unknown-model"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    partial = "-partial" if (args.case or args.arm or args.runs != 3) else ""
    # Results go under a per-profile directory. Writing both corpora to one path would have the
    # second run overwrite the first on the same day against the same model.
    results_dir = RESULTS_DIR if args.profile == "requirement-zero" else (
        EVAL_DIR / args.profile / "results")
    results_dir.mkdir(parents=True, exist_ok=True)
    out = results_dir / f"{stamp}-{model_slug}{partial}.json"
    out.write_text(json.dumps({
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "harness": "eval/run_eval.py",
        "profile": args.profile,
        "skill_under_test": str(profile["skill_path"].relative_to(REPO_ROOT)),  # type: ignore[union-attr]
        "verdict_vocabulary": list(profile["verdicts"]),  # type: ignore[arg-type]
        "cli": "claude",
        "cli_version": subprocess.run(["claude", "--version"], capture_output=True, text=True)
                        .stdout.strip() or None,
        "model_flag": "sonnet",
        "models_observed": models,
        "runs_per_arm_per_case": args.runs,
        "arms": arms,
        # Machine-verified identity of the skill under test: survives file moves and does not rot
        # the way a hand-typed commit SHA does.
        "skill_body_sha256": hashlib.sha256(skill.encode("utf-8")).hexdigest(),
        "skill_body_chars": len(skill),
        # Flags that make the run reproducible by a stranger, regardless of working directory.
        "isolation_flags": ["--tools", "", "--safe-mode"],
        "filters": {"case": args.case, "arm": args.arm},
        "cases": [{"file": c["file"], **c["meta"]} for c in cases],  # type: ignore[dict-item]
        "summary": summary,
        "runs": records,
    }, indent=2) + "\n", encoding="utf-8")

    print_table(summary, arms)
    print(f"\nwrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
