"""R4 ``build_raw_request_for_r4`` and modular ``resolve_jd_for_lanes`` share JD normalization."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.jd_resolution import (
    build_canonical_jd_payload,
    canonical_jd_digest,
    resolve_jd_for_lanes,
)
from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4


def _assert_parity(
    *,
    jd_raw: str,
    target_company: str,
    target_role: str,
    r4_jd_path: Path,
) -> None:
    r4_jd_path.write_text(jd_raw, encoding="utf-8")
    raw = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        jd=str(r4_jd_path),
    )
    expected = build_canonical_jd_payload(
        jd_raw,
        target_company=target_company,
        target_role=target_role,
    )
    assert raw["jd_payload"] == expected
    assert raw["jd_hash"] == canonical_jd_digest(expected)

    lane = resolve_jd_for_lanes(
        job_description_text=jd_raw,
        target_company=target_company,
        target_role=target_role,
    )
    assert lane.jd_digest == raw["jd_hash"]
    assert lane.description == expected["description"]
    assert lane.title == expected["title"]
    assert lane.company == expected["company"]


def test_plain_text_jd_parity(tmp_path: Path) -> None:
    body = "Scale distributed inference; own on-call for model serving.\n"
    _assert_parity(
        jd_raw=body,
        target_company="Acme Labs",
        target_role="Senior MLE",
        r4_jd_path=tmp_path / "jd.txt",
    )


def test_json_jd_title_description_company_parity(tmp_path: Path) -> None:
    blob = json.dumps(
        {
            "title": "Director, AI Platform",
            "description": "Agentic systems and governance.",
            "company": "Contoso",
        }
    )
    _assert_parity(
        jd_raw=blob,
        target_company="IgnoredFromCLI",
        target_role="VP Eng",
        r4_jd_path=tmp_path / "jd.json",
    )


def test_empty_jd_material_fallback_parity(tmp_path: Path) -> None:
    """Missing-file path yields non-JSON raw string; R4 and resolver agree."""
    p = tmp_path / "missing_jd.txt"
    raw_req = build_raw_request_for_r4(
        target_company="Co",
        target_role="Role",
        jd=str(p),
    )
    expected = build_canonical_jd_payload(
        str(p),
        target_company="Co",
        target_role="Role",
    )
    assert raw_req["jd_payload"] == expected
    lane = resolve_jd_for_lanes(
        job_description_text=str(p),
        target_company="Co",
        target_role="Role",
    )
    assert lane.jd_digest == raw_req["jd_hash"]
