"""E2E enforcement tests for apps_rg cross-company contamination guards.

Plan reference: post-2026-05-05 hardening of apps_rg/__main__.py to prevent
prior-resume / prior-company artifacts from silently bleeding into a new run.

Invariant under test:
    A run for company X cannot use any artifact (briefing, JD) whose declared
    `company` field is not X. Mismatch is fatal at intake — neither L0 nor
    downstream layers ever see the contaminated input. --target-company and
    --target-role must be supplied explicitly; auto-deriving them from the
    hand-authored default JSONs is forbidden.

These tests pin behavior via the `_assert_artifact_matches_company` helper
and the argparse-required hard errors in `main()`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.__main__ import _assert_artifact_matches_company

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Unit-level tests for the contamination guard helper
# ---------------------------------------------------------------------------


def test_guard_noop_when_path_missing(tmp_path: Path) -> None:
    """Missing file is the L0 gate's job — guard must not raise."""
    _assert_artifact_matches_company(
        tmp_path / "does-not-exist.json", "Brown & Brown", "manual_brief"
    )


def test_guard_noop_when_target_company_empty(tmp_path: Path) -> None:
    """Empty target_company means caller hasn't validated yet — guard skips."""
    p = tmp_path / "brief.json"
    p.write_text(json.dumps({"company": "Blend360"}), encoding="utf-8")
    _assert_artifact_matches_company(p, "", "manual_brief")


def test_guard_noop_when_artifact_has_no_company(tmp_path: Path) -> None:
    """Master candidate profiles carry no `company` key — guard skips."""
    p = tmp_path / "candidate.yaml"
    p.write_text("name: Jane Doe\nskills: [python]\n", encoding="utf-8")
    _assert_artifact_matches_company(p, "Brown & Brown", "candidate")


def test_guard_passes_when_company_matches(tmp_path: Path) -> None:
    """Matching company → no-op."""
    p = tmp_path / "brief.json"
    p.write_text(json.dumps({"company": "Brown & Brown"}), encoding="utf-8")
    _assert_artifact_matches_company(p, "Brown & Brown", "manual_brief")


def test_guard_passes_when_company_matches_case_insensitive(tmp_path: Path) -> None:
    """Case differences must not trigger the guard."""
    p = tmp_path / "brief.json"
    p.write_text(json.dumps({"company": "BROWN & BROWN"}), encoding="utf-8")
    _assert_artifact_matches_company(p, "brown & brown", "manual_brief")


def test_guard_raises_on_company_mismatch_json(tmp_path: Path) -> None:
    """JSON briefing with mismatched company → SystemExit."""
    p = tmp_path / "brief.json"
    p.write_text(json.dumps({"company": "Blend360"}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        _assert_artifact_matches_company(p, "Brown & Brown", "manual_brief")
    msg = str(exc.value)
    assert "FATAL" in msg
    assert "Blend360" in msg
    assert "Brown & Brown" in msg
    assert "manual_brief" in msg


def test_guard_raises_on_company_mismatch_yaml(tmp_path: Path) -> None:
    """YAML briefing with mismatched company → SystemExit."""
    p = tmp_path / "brief.yaml"
    p.write_text("company: Blend360\nfetched_at: '2026-05-01T00:00:00Z'\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        _assert_artifact_matches_company(p, "Brown & Brown", "manual_brief")
    assert "FATAL" in str(exc.value)


def test_guard_noop_on_unsupported_extension(tmp_path: Path) -> None:
    """Non-JSON/YAML file with mismatched name shouldn't be parsed."""
    p = tmp_path / "brief.txt"
    p.write_text("company: Blend360", encoding="utf-8")
    _assert_artifact_matches_company(p, "Brown & Brown", "manual_brief")


def test_guard_noop_on_corrupt_json(tmp_path: Path) -> None:
    """Corrupt JSON should not raise (guard is fail-soft on parse errors)."""
    p = tmp_path / "brief.json"
    p.write_text("{not valid json", encoding="utf-8")
    _assert_artifact_matches_company(p, "Brown & Brown", "manual_brief")


def test_guard_noop_on_non_dict_yaml(tmp_path: Path) -> None:
    """YAML that parses to a list (not a dict) → guard skips."""
    p = tmp_path / "brief.yaml"
    p.write_text("- item1\n- item2\n", encoding="utf-8")
    _assert_artifact_matches_company(p, "Brown & Brown", "manual_brief")


# ---------------------------------------------------------------------------
# E2E subprocess tests for `python -m apps_rg`
# ---------------------------------------------------------------------------


def _run_apps_rg(*args: str) -> subprocess.CompletedProcess:
    """Invoke `python -m apps_rg` with the given args; capture stdout+stderr."""
    return subprocess.run(
        [sys.executable, "-m", "apps_rg", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_e2e_missing_target_company_triggers_wizard() -> None:
    """No --target-company → wizard mode (cascade-prompts) writes sentinel; exit 7."""
    result = _run_apps_rg(
        "--target-role",
        "Senior Vice President, IT Strategy & Innovation",
        "--cascade-prompts",
    )
    # Wizard mode with cascade-prompts writes sentinel and exits 7
    assert result.returncode == 7
    combined = result.stdout + result.stderr
    assert "mandatory" in combined.lower() or "cascade" in combined.lower() or "sentinel" in combined.lower()


def test_e2e_missing_target_role_triggers_wizard() -> None:
    """No --target-role → wizard mode (cascade-prompts) writes sentinel; exit 7."""
    result = _run_apps_rg("--target-company", "Brown & Brown", "--cascade-prompts")
    # Wizard mode with cascade-prompts writes sentinel and exits 7
    assert result.returncode == 7
    combined = result.stdout + result.stderr
    assert "mandatory" in combined.lower() or "cascade" in combined.lower() or "sentinel" in combined.lower()


def test_e2e_no_args_triggers_wizard() -> None:
    """No args at all → wizard mode (cascade-prompts) writes sentinel; exit 7."""
    result = _run_apps_rg("--cascade-prompts")
    # Wizard mode with cascade-prompts writes sentinel and exits 7
    assert result.returncode == 7
    combined = result.stdout + result.stderr
    assert "mandatory" in combined.lower() or "cascade" in combined.lower() or "sentinel" in combined.lower()


def test_e2e_default_artifacts_for_different_company_trigger_guard(
    tmp_path: Path,
) -> None:
    """Both --jd and --manual-brief default to hand-authored files for one
    specific company. Running for any OTHER company must trigger the
    contamination guard at intake before L0 sees the request. Either guard
    firing (jd or manual_brief) satisfies the invariant.
    """
    default_brief = REPO_ROOT / "apps_rg" / "scripts" / "company_research.json"
    if not default_brief.exists():
        pytest.skip("default brief not present in this checkout")
    default_company = json.loads(default_brief.read_text(encoding="utf-8")).get("company", "")
    if not default_company:
        pytest.skip("default brief carries no company field")

    other_company = "Definitely Not " + default_company
    result = _run_apps_rg(
        "--target-company",
        other_company,
        "--target-role",
        "Senior Engineer",
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "FATAL" in combined
    # Either default artifact's guard is acceptable proof of invariant.
    assert ("manual_brief" in combined) or ("jd" in combined)
    assert default_company in combined
    assert other_company in combined


def test_e2e_jd_for_different_company_triggers_guard(tmp_path: Path) -> None:
    """A JD JSON whose `company` field doesn't match --target-company must
    trip the guard at intake.
    """
    bad_jd = tmp_path / "bad_jd.json"
    bad_jd.write_text(
        json.dumps({"company": "Acme Co", "title": "Engineer"}), encoding="utf-8"
    )
    result = _run_apps_rg(
        "--target-company",
        "Brown & Brown",
        "--target-role",
        "Engineer",
        "--jd",
        str(bad_jd),
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "FATAL" in combined
    assert "jd" in combined
    assert "Acme Co" in combined
    assert "Brown & Brown" in combined


def test_e2e_nonexistent_brief_falls_through_to_l0_gate(tmp_path: Path) -> None:
    """A briefing path that does NOT exist must NOT silently substitute the
    default file. It must pass through to the L0 prerequisite gate which
    routes to apps_research (the canonical happy path when no briefing exists).

    A matching --jd is supplied so the JD guard does not pre-empt the test.
    """
    matching_jd = tmp_path / "brown_brown_jd.json"
    matching_jd.write_text(
        json.dumps({"company": "Brown & Brown", "title": "SVP, IT Strategy"}),
        encoding="utf-8",
    )
    nonexistent = tmp_path / "no_briefing_for_brown_brown.json"
    assert not nonexistent.exists()
    result = _run_apps_rg(
        "--target-company",
        "Brown & Brown",
        "--target-role",
        "Senior Vice President, IT Strategy & Innovation",
        "--jd",
        str(matching_jd),
        "--manual-brief",
        str(nonexistent),
    )
    # Exits non-zero because briefing is missing — but the message must be
    # the L0 routing message, NOT the contamination guard, NOT a silent
    # success on the default Blend360 file.
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "FATAL" not in combined  # contamination guard did not fire
    assert (
        "MISSING" in combined
        or "apps_research" in combined
        or "briefing missing" in combined.lower()
    )


def test_e2e_matching_brief_passes_intake_guard(tmp_path: Path) -> None:
    """A briefing whose company matches --target-company passes the guard
    and reaches the L0 prerequisite gate (which may then proceed or fail
    on other criteria — that's not what this test pins).

    A matching --jd is supplied so the JD guard does not pre-empt the test.
    """
    matching_jd = tmp_path / "brown_brown_jd.json"
    matching_jd.write_text(
        json.dumps({"company": "Brown & Brown", "title": "SVP, IT Strategy"}),
        encoding="utf-8",
    )
    brief = tmp_path / "matching_brief.json"
    brief.write_text(
        json.dumps(
            {
                "company": "Brown & Brown",
                "fetched_at": "2026-05-01T00:00:00Z",
                "overview": {"founded": 1939, "size_band": "10001+"},
                "cultural_cues": ["meritocracy"],
                "recent_moves": [{"date": "2026-04", "event": "test"}],
            }
        ),
        encoding="utf-8",
    )
    result = _run_apps_rg(
        "--target-company",
        "Brown & Brown",
        "--target-role",
        "Senior Vice President, IT Strategy & Innovation",
        "--jd",
        str(matching_jd),
        "--manual-brief",
        str(brief),
    )
    combined = result.stdout + result.stderr
    # The contamination guard MUST NOT fire on matching artifacts.
    assert "FATAL: manual_brief" not in combined
    assert "FATAL: jd" not in combined
