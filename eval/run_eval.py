#!/usr/bin/env python3
"""Compare agent verdicts on the same requirement cases with and without Requirement Zero.

Two arms, identical user prompts. The only difference is that the `skill` arm gets the
repository's SKILL.md appended to the system prompt. Standard library only; shells out to
the `claude` CLI.

Runs are isolated with `--safe-mode` (no ambient CLAUDE.md discovery from the working directory)
and `--tools ""` (tools removed from the model's schema). Both matter for validity: see
eval/README.md "Isolation".

    python3 eval/run_eval.py                      # full matrix: 6 cases x 2 arms x 3 runs
    python3 eval/run_eval.py --runs 1 --case 01   # one cheap pair of calls
    python3 eval/run_eval.py --self-test          # verdict-extraction checks, no calls
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
CASES_DIR = EVAL_DIR / "cases"
RESULTS_DIR = EVAL_DIR / "results"
SKILL_PATH = REPO_ROOT / "SKILL.md"

VERDICTS = ("BUILD HARD", "DELETE", "REDUCE", "DEFER", "BUILD")  # BUILD HARD first: longest match wins
UNPARSEABLE = "UNPARSEABLE"  # model answered, but no readable VERDICT line: a real non-match
ERRORED = "ERRORED"          # CLI/harness failure: excluded from match-rate denominators
FALSE_REJECTIONS = ("DELETE", "DEFER")  # wrong when the expected verdict is BUILD or BUILD HARD
CALL_TIMEOUT_S = 300

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


def load_cases(case_filter: str | None) -> list[dict[str, object]]:
    cases = []
    for path in sorted(CASES_DIR.glob("*.md")):
        if case_filter and not path.name.startswith(case_filter):
            continue
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        missing = {"id", "expected_verdict", "case_type", "example"} - meta.keys()
        if missing:
            raise ValueError(f"{path.name}: missing frontmatter keys {sorted(missing)}")
        if meta["expected_verdict"] not in VERDICTS:
            raise ValueError(f"{path.name}: bad expected_verdict {meta['expected_verdict']!r}")
        if not (path.parent / meta["example"]).resolve().is_file():
            raise ValueError(f"{path.name}: example path does not resolve: {meta['example']}")
        cases.append({"file": path.name, "meta": meta, "body": body})
    if not cases:
        raise SystemExit(f"no cases matched {case_filter!r}")
    return cases


def skill_body() -> str:
    """The shipped skill, read from disk at run time so the eval always tests what ships."""
    _, body = parse_frontmatter(SKILL_PATH.read_text(encoding="utf-8"))
    if not body.strip():
        raise SystemExit(  # otherwise both arms silently become identical and report a null result
            f"{SKILL_PATH.name} has an empty body: the skill arm would be identical to baseline."
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


def extract_verdict(text: str) -> str:
    """Read the final `VERDICT:` line. Never guess: anything else is UNPARSEABLE."""
    for line in reversed(text.strip().splitlines()):
        line = line.strip().strip(_TAIL_STRIP)
        if not line.upper().lstrip(_TAIL_STRIP).startswith("VERDICT"):
            continue
        tail = _normalise_tail(line.split(":", 1)[-1])
        for verdict in VERDICTS:  # BUILD HARD before BUILD
            if tail.startswith(verdict):
                return verdict
        return UNPARSEABLE
    return UNPARSEABLE


# (input, expected) pairs for --self-test. Costs nothing and defends verdict extraction, which
# every other metric depends on.
SELF_TEST_CASES = (
    ("VERDICT: BUILD HARD", "BUILD HARD"),
    ("VERDICT: BUILD **HARD**", "BUILD HARD"),
    ("VERDICT: BUILD  HARD", "BUILD HARD"),
    ("VERDICT: BUILD-HARD", "BUILD HARD"),
    ("VERDICT: BUILD_HARD", "BUILD HARD"),
    ("VERDICT: BUILD HARD", "BUILD HARD"),
    ("VERDICT: `BUILD HARD`", "BUILD HARD"),
    ("> VERDICT: BUILD HARD", "BUILD HARD"),
    ("**VERDICT: BUILD HARD**", "BUILD HARD"),
    ("prose\n\nVERDICT: BUILD HARD.", "BUILD HARD"),
    ("VERDICT: BUILD", "BUILD"),
    ("verdict: build", "BUILD"),
    ("**VERDICT: DELETE**", "DELETE"),
    ("VERDICT: `DEFER`", "DEFER"),
    ("VERDICT: REDUCE", "REDUCE"),
    ("VERDICT: maybe", UNPARSEABLE),
    ("no verdict line at all", UNPARSEABLE),
    ("", UNPARSEABLE),
    ("VERDICT: BUILD HARD\nVERDICT: DELETE", "DELETE"),  # last line wins
)


def self_test() -> int:
    failures = [
        (raw, expected, got)
        for raw, expected in SELF_TEST_CASES
        if (got := extract_verdict(raw)) != expected
    ]
    for raw, expected, got in failures:
        print(f"FAIL {raw!r}: expected {expected!r}, got {got!r}")
    print(f"{len(SELF_TEST_CASES) - len(failures)}/{len(SELF_TEST_CASES)} "
          f"verdict-extraction cases pass")
    return 1 if failures else 0


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


def run_once(case: dict[str, object], arm: str, skill: str, run_index: int) -> dict[str, object]:
    meta = case["meta"]  # type: ignore[index]
    expected = meta["expected_verdict"]
    record: dict[str, object] = {
        "case": case["file"], "arm": arm, "run": run_index, "expected_verdict": expected,
    }
    outcome = call_claude(
        PROMPT_TEMPLATE.format(body=case["body"]), skill if arm == "skill" else None
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
    verdict = extract_verdict(text)
    record.update(
        # Only whitelisted fields are kept: no session ids, uuids, or local paths.
        verdict=verdict,
        matched=verdict == expected,
        false_rejection=expected in ("BUILD", "BUILD HARD") and verdict in FALSE_REJECTIONS,
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
            print(f"\n  *** GUARD FAILED: {arm} arm produced DELETE/DEFER on the safety case "
                  f"{t['guard_failures']} of {t['guard_scored_runs']} scored run(s). ***")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3, help="runs per arm per case (default 3)")
    parser.add_argument("--case", help="only cases whose filename starts with this, e.g. 01")
    parser.add_argument("--arm", choices=("baseline", "skill"), help="only this arm")
    parser.add_argument("--self-test", action="store_true",
                        help="check verdict extraction against known tricky strings; makes no calls")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    cases = load_cases(args.case)
    arms = [args.arm] if args.arm else ["baseline", "skill"]
    skill = skill_body()
    total_calls = len(cases) * len(arms) * args.runs
    print(f"{len(cases)} case(s) x {len(arms)} arm(s) x {args.runs} run(s) = {total_calls} CLI calls")

    records: list[dict[str, object]] = []
    for run_index in range(1, args.runs + 1):
        for case in cases:
            for arm in arms:
                record = run_once(case, arm, skill, run_index)
                records.append(record)
                print(f"  run {run_index} {case['file'][:2]} {arm:<9} -> {record['verdict']}"
                      + (f"  ERROR {record['error']}" if "error" in record else ""))
                sys.stdout.flush()

    summary = summarise(records, cases, arms)
    models = sorted({str(r.get("model")) for r in records if r.get("model")})
    model_slug = re.sub(r"[^A-Za-z0-9.-]+", "-", models[0]) if models else "unknown-model"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    partial = "-partial" if (args.case or args.arm or args.runs != 3) else ""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{stamp}-{model_slug}{partial}.json"
    out.write_text(json.dumps({
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "harness": "eval/run_eval.py",
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
