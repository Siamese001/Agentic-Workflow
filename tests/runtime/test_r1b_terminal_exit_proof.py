"""Tests — W1 phase 2 R1B TerminalRetPacket/ExitReviewPacket/X3 proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_r1b_terminal_exit.py"
ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "r1b_terminal_exit_proof.json"


def _run() -> int:
    return subprocess.run(
        [sys.executable, str(PROBE)], cwd=str(REPO_ROOT),
        timeout=30, check=False, capture_output=True,
    ).returncode


def _read() -> dict:
    _run()
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class TestProbeRuns:
    def test_probe_exits_zero(self):
        assert _run() == 0


class TestInvariant1TerminalRetPacket:
    def test_terminal_ret_packet_exists(self):
        a = _read()
        assert a["details"]["TerminalRetPacket"]["type_importable"] is True
        assert a["details"]["TerminalRetPacket"]["is_dataclass"] is True

    def test_invariant_1_passes(self):
        a = _read()
        assert a["invariants"]["1_terminal_ret_packet_exists_and_shaped"] is True


class TestInvariant2And3ExitReviewPacket:
    def test_exit_review_packet_exists(self):
        a = _read()
        assert a["details"]["ExitReviewPacket"]["type_importable"] is True
        assert a["details"]["ExitReviewPacket"]["is_dataclass"] is True

    def test_invariant_2_3_passes(self):
        a = _read()
        assert a["invariants"]["2_and_3_exit_review_packet_exists_and_shaped"] is True


class TestInvariant4X3ExactlyOne:
    def test_v6_disposition_has_all_six_members(self):
        a = _read()
        x3 = a["details"]["X3_dispositions"]
        assert x3["enum_importable"] is True
        assert x3["members_match"] is True
        assert set(x3["actual_members"].values()) >= {
            "X3A", "X3B", "X3C", "X3D", "X3E", "X3F",
        }

    def test_invariant_4_passes(self):
        a = _read()
        assert a["invariants"]["4_exactly_one_x3_disposition_per_run"] is True


class TestInvariant5CacheHitNoBypassOrL2:
    def test_cache_hit_no_bypass_fields_in_schema(self):
        a = _read()
        no_bypass = a["details"]["cache_hit_no_bypass"]
        assert no_bypass["passes"] is True
        assert no_bypass["forbidden_bypass_fields_present"] == []

    def test_terminal_no_l2_execution(self):
        a = _read()
        no_l2 = a["details"]["terminal_no_l2"]
        assert no_l2["passes"] is True
        assert no_l2["forbidden_l2_members"] == []

    def test_invariant_5a_5b_passes(self):
        a = _read()
        assert a["invariants"]["5a_cache_hit_does_not_bypass_exit"] is True
        assert a["invariants"]["5b_terminal_does_not_execute_l2"] is True


class TestOverall:
    def test_all_five_invariants_pass(self):
        a = _read()
        assert a["all_five_pass"] is True
        assert a["overall_status"] == "PASS"

    def test_scope_boundary_respected(self):
        a = _read()
        assert "R1B_INTEGRATED_RUNTIME_PROOF remains NOT_APPLICABLE" in a["scope_boundary"]

    def test_no_final_acceptance_status_field(self):
        a = _read()
        assert "final_acceptance_status" not in a
        assert a["anti_cheat_rules_honored"]["probe_did_not_write_sidecar"] is True
