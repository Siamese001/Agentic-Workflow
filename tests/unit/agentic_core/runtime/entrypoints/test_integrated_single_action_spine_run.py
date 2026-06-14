"""Unit tests for agentic_core.runtime.entrypoints.integrated_single_action_spine_run.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 spine entrypoint.
``integrated_single_action_spine_run`` (fan_in=15) is the R4 single-action spine
entrypoint. Full-pipeline execution is integration-scoped; here we cover the pure,
deterministic helpers + result contract + fail-soft route resolution.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
    CHAIN_KIND,
    ROUTE_FAMILY,
    ROUTE_ID,
    SingleActionSpineRunResult,
    _load_route_id_for_app,
    _looks_like_content_sha256_digest,
    _normalize_digest_literal,
    _sha256_file,
)


class TestConstants:
    def test_r4_single_action_identity(self) -> None:
        assert CHAIN_KIND == "R4_SINGLE_ACTION"
        assert ROUTE_FAMILY == "R4_SINGLE_ACTION"
        assert ROUTE_ID == "R4_SINGLE_ACTION"


class TestSingleActionSpineRunResult:
    def test_construction_and_defaults(self) -> None:
        r = SingleActionSpineRunResult(
            run_id="run-1",
            request_id="req-1",
            route_id=ROUTE_ID,
            x3_disposition="X3D_ALLOW_FINISH",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=Path("/tmp/run-1"),
        )
        assert r.route_id == "R4_SINGLE_ACTION"
        assert r.fault == ""
        assert r.producer_component  # default non-empty

    def test_frozen(self) -> None:
        r = SingleActionSpineRunResult(
            run_id="r", request_id="q", route_id=ROUTE_ID,
            x3_disposition="X3E_SAFE_ABSTAIN", terminal_r5=True,
            terminal_r5_reason="ood", artifact_dir=Path("."),
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            r.run_id = "x"  # type: ignore[misc]


class TestLoadRouteIdForApp:
    def test_empty_app_returns_default_route(self) -> None:
        assert _load_route_id_for_app("") == ROUTE_ID

    def test_missing_registry_is_fail_soft(self) -> None:
        # No such app tree → fail-soft to the module ROUTE_ID constant.
        assert _load_route_id_for_app("apps_does_not_exist_xyz") == ROUTE_ID


class TestSha256File:
    def test_missing_file_returns_none(self, tmp_path: Path) -> None:
        assert _sha256_file(tmp_path / "nope.bin") is None

    def test_hashes_existing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "x.bin"
        p.write_bytes(b"hello world")
        expected = "sha256:" + hashlib.sha256(b"hello world").hexdigest()
        assert _sha256_file(p) == expected


class TestLooksLikeContentSha256Digest:
    def test_bare_64_hex_is_digest(self) -> None:
        assert _looks_like_content_sha256_digest("a" * 64) is True

    def test_prefixed_64_hex_is_digest(self) -> None:
        assert _looks_like_content_sha256_digest("sha256:" + "b" * 64) is True

    @pytest.mark.parametrize(
        "bad",
        ["", "abc", "a" * 63, "a" * 65, "sha256:" + "a" * 63, "z" * 64],
    )
    def test_non_digests_rejected(self, bad: str) -> None:
        assert _looks_like_content_sha256_digest(bad) is False


class TestNormalizeDigestLiteral:
    def test_empty_stays_empty(self) -> None:
        assert _normalize_digest_literal("") == ""

    def test_bare_gets_prefixed_and_lowercased(self) -> None:
        assert _normalize_digest_literal("ABCDEF") == "sha256:abcdef"

    def test_already_prefixed_unchanged(self) -> None:
        assert _normalize_digest_literal("sha256:deadbeef") == "sha256:deadbeef"
