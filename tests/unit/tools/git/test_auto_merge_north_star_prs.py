"""Unit tests for tools/git/auto_merge_north_star_prs.py.

The GitHub REST API is FULLY MOCKED — no live HTTP. We monkeypatch the four read helpers
and ``merge_pr`` so the decision logic, fail-soft contract, squash refusal, and structured
summary are exercised hermetically.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "tools" / "git" / "auto_merge_north_star_prs.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("auto_merge_north_star_prs", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


amns = _load_module()


# --------------------------------------------------------------------------- #
# Fixtures / builders
# --------------------------------------------------------------------------- #
def _pr(number, ref="claude/apps_rg-fix", draft=False, labels=None):
    return {
        "number": number,
        "draft": draft,
        "labels": [{"name": n} for n in (labels or [])],
        "head": {"ref": ref, "sha": f"sha{number}"},
    }


_CLEAN_DETAIL = {"mergeable": True, "mergeable_state": "clean"}
_GREEN_STATUS = {"statuses": [{"context": "ci", "state": "success"}]}
_GREEN_CHECKS = {"check_runs": [{"name": "build", "status": "completed", "conclusion": "success"}]}
_ENABLED_STATE = {"enabled": True, "lanes_passing": 1, "lanes_total": 11}


# --------------------------------------------------------------------------- #
# Relevance + state
# --------------------------------------------------------------------------- #
def test_is_north_star_branch():
    assert amns.is_north_star_branch("claude/apps_rg-lane-fix")
    assert amns.is_north_star_branch("apps_lic/sender")
    assert amns.is_north_star_branch("feature/apps_eval-thing")
    assert not amns.is_north_star_branch("chore/governance-cleanup")
    assert not amns.is_north_star_branch("")


def test_north_prefixes_match_gate():
    # The tool must mirror the gate's relevance definition verbatim.
    expected = (
        "apps_rg/", "apps_lic/", "apps_eval/",
        "tests/unit/apps_rg", "tests/apps_rg",
        "tests/unit/apps_lic", "tests/apps_lic",
        "tests/unit/apps_eval", "tests/apps_eval",
    )
    assert amns._NORTH_PREFIXES == expected


def test_load_state_fail_soft(tmp_path):
    assert amns.load_north_star_state(tmp_path / "nope.json") == {}
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert amns.load_north_star_state(bad) == {}


def test_north_star_enabled():
    assert amns.north_star_enabled({"enabled": True})
    assert not amns.north_star_enabled({"enabled": False})
    assert not amns.north_star_enabled({})


# --------------------------------------------------------------------------- #
# get_token
# --------------------------------------------------------------------------- #
def test_get_token_precedence():
    assert amns.get_token({"GITHUB_TOKEN": "a", "GH_TOKEN": "b"}) == "a"
    assert amns.get_token({"GH_TOKEN": "b"}) == "b"
    assert amns.get_token({}) is None
    assert amns.get_token({"GITHUB_TOKEN": "   "}) is None


# --------------------------------------------------------------------------- #
# checks_all_green
# --------------------------------------------------------------------------- #
def test_checks_all_green_happy():
    ok, why = amns.checks_all_green(_GREEN_STATUS, _GREEN_CHECKS)
    assert ok and why == ""


def test_checks_all_green_skipped_ok():
    checks = {"check_runs": [{"name": "x", "status": "completed", "conclusion": "skipped"}]}
    ok, _ = amns.checks_all_green({}, checks)
    assert ok


def test_checks_pending_status_fails():
    ok, why = amns.checks_all_green({"statuses": [{"context": "ci", "state": "pending"}]}, {})
    assert not ok and "pending" in why


def test_checks_failed_run_fails():
    checks = {"check_runs": [{"name": "build", "status": "completed", "conclusion": "failure"}]}
    ok, why = amns.checks_all_green({}, checks)
    assert not ok and "failure" in why


def test_checks_incomplete_run_fails():
    checks = {"check_runs": [{"name": "build", "status": "in_progress", "conclusion": None}]}
    ok, why = amns.checks_all_green({}, checks)
    assert not ok and "not completed" in why


# --------------------------------------------------------------------------- #
# evaluate_pr — the decision matrix
# --------------------------------------------------------------------------- #
def test_evaluate_merge_happy():
    decision, reason = amns.evaluate_pr(_pr(1), _CLEAN_DETAIL, _GREEN_STATUS, _GREEN_CHECKS, _ENABLED_STATE)
    assert decision == "merge"
    assert "north-star" in reason


def test_evaluate_skip_draft():
    decision, reason = amns.evaluate_pr(_pr(2, draft=True), _CLEAN_DETAIL, _GREEN_STATUS, _GREEN_CHECKS, _ENABLED_STATE)
    assert decision == "skip" and "draft" in reason


@pytest.mark.parametrize("label", ["meta", "governance", "hold", "do-not-merge"])
def test_evaluate_skip_manual_labels(label):
    decision, reason = amns.evaluate_pr(
        _pr(3, labels=[label]), _CLEAN_DETAIL, _GREEN_STATUS, _GREEN_CHECKS, _ENABLED_STATE
    )
    assert decision == "skip" and "manual merge" in reason


def test_evaluate_skip_off_north_star():
    decision, reason = amns.evaluate_pr(
        _pr(4, ref="chore/governance"), _CLEAN_DETAIL, _GREEN_STATUS, _GREEN_CHECKS, _ENABLED_STATE
    )
    assert decision == "skip" and "not north-star-relevant" in reason


def test_evaluate_skip_north_star_disabled():
    decision, reason = amns.evaluate_pr(_pr(5), _CLEAN_DETAIL, _GREEN_STATUS, _GREEN_CHECKS, {"enabled": False})
    assert decision == "skip" and "enabled != true" in reason


def test_evaluate_skip_conflicts():
    detail = {"mergeable": False, "mergeable_state": "dirty"}
    decision, reason = amns.evaluate_pr(_pr(6), detail, _GREEN_STATUS, _GREEN_CHECKS, _ENABLED_STATE)
    assert decision == "skip" and "not mergeable" in reason


def test_evaluate_skip_mergeability_unknown():
    detail = {"mergeable": None, "mergeable_state": "unknown"}
    decision, reason = amns.evaluate_pr(_pr(7), detail, _GREEN_STATUS, _GREEN_CHECKS, _ENABLED_STATE)
    assert decision == "skip" and "unknown" in reason


def test_evaluate_skip_unstable_state():
    detail = {"mergeable": True, "mergeable_state": "unstable"}
    decision, reason = amns.evaluate_pr(_pr(8), detail, _GREEN_STATUS, _GREEN_CHECKS, _ENABLED_STATE)
    assert decision == "skip" and "unstable" in reason


def test_evaluate_skip_red_ci():
    red = {"check_runs": [{"name": "build", "status": "completed", "conclusion": "failure"}]}
    decision, reason = amns.evaluate_pr(_pr(9), _CLEAN_DETAIL, _GREEN_STATUS, red, _ENABLED_STATE)
    assert decision == "skip" and "CI not green" in reason


# --------------------------------------------------------------------------- #
# run() — full loop with the API mocked
# --------------------------------------------------------------------------- #
def _wire_mocks(monkeypatch, prs, *, detail=None, combined=None, checks=None, merge_result=(True, "ok")):
    monkeypatch.setattr(amns, "list_open_prs", lambda o, r, t: prs)
    monkeypatch.setattr(amns, "get_pr_detail", lambda o, r, n, t: detail if detail is not None else _CLEAN_DETAIL)
    monkeypatch.setattr(amns, "get_combined_status", lambda o, r, s, t: combined if combined is not None else _GREEN_STATUS)
    monkeypatch.setattr(amns, "get_check_runs", lambda o, r, s, t: checks if checks is not None else _GREEN_CHECKS)
    merges: list[tuple] = []

    def _merge(o, r, n, m, t):
        merges.append((n, m))
        return merge_result

    monkeypatch.setattr(amns, "merge_pr", _merge)
    return merges


def test_run_merges_eligible(monkeypatch):
    merges = _wire_mocks(monkeypatch, [_pr(10), _pr(11, ref="chore/x")])
    summary = amns.run("o", "r", "merge", dry_run=False, token="tok", state=_ENABLED_STATE)
    assert [m["number"] for m in summary["merged"]] == [10]
    assert any("not north-star" in s["reason"] for s in summary["skipped"])
    assert merges == [(10, "merge")]


def test_run_dry_run_merges_nothing(monkeypatch):
    merges = _wire_mocks(monkeypatch, [_pr(12)])
    summary = amns.run("o", "r", "merge", dry_run=True, token="tok", state=_ENABLED_STATE)
    assert summary["dry_run"] is True
    assert summary["merged"] and "DRY-RUN" in summary["merged"][0]["reason"]
    assert merges == []  # never called in dry-run


def test_run_merge_failure_routes_to_blocked(monkeypatch):
    _wire_mocks(monkeypatch, [_pr(13)], merge_result=(False, "merge HTTP 405: not mergeable"))
    summary = amns.run("o", "r", "merge", dry_run=False, token="tok", state=_ENABLED_STATE)
    assert not summary["merged"]
    assert summary["blocked"] and summary["blocked"][0]["number"] == 13


def test_run_uses_rebase_method(monkeypatch):
    merges = _wire_mocks(monkeypatch, [_pr(14)])
    amns.run("o", "r", "rebase", dry_run=False, token="tok", state=_ENABLED_STATE)
    assert merges == [(14, "rebase")]


# --------------------------------------------------------------------------- #
# main() — CLI contract
# --------------------------------------------------------------------------- #
def test_main_squash_is_usage_error(capsys):
    assert amns.main(["--method", "squash"]) == 2
    err = capsys.readouterr().err
    assert "FORBIDDEN" in err


def test_main_no_token_is_blocked_exit0(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert amns.main([]) == 0
    err = capsys.readouterr().err
    assert "BLOCKED" in err


def test_main_default_method_is_merge():
    args = amns.build_parser().parse_args([])
    assert args.method == "merge"
    assert args.owner == "Siamese001"
    assert args.repo == "Agentic-Workflow"
    assert args.trunk == "main"


def test_main_happy_exit0(monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    _wire_mocks(monkeypatch, [_pr(15)])
    monkeypatch.setattr(amns, "load_north_star_state", lambda *a, **k: _ENABLED_STATE)
    assert amns.main(["--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "auto_merge_north_star_prs" in out and "MERGED" in out


def test_squash_never_passed_to_merge_pr(monkeypatch):
    # Defense-in-depth: even if run() were called with 'squash', main() blocks it first;
    # verify main() never reaches the merge loop on squash.
    called = {"ran": False}
    monkeypatch.setattr(amns, "run", lambda *a, **k: called.__setitem__("ran", True) or {})
    amns.main(["--method", "squash"])
    assert called["ran"] is False
