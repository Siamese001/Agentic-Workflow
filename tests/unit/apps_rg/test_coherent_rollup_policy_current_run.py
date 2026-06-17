from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime.aggregation import coherent_rollup_policy as policy_mod


def _patch_policy_inputs(monkeypatch, *, same_date_prefix_coherent: bool) -> None:
    def _fake_build_fingerprint_from_rollup(**kwargs):
        fingerprint = {
            "same_date_prefix_coherent": same_date_prefix_coherent,
            "same_run_coherent": False,
            "jd_digest_coherent": "OK",
            "briefing_digest_coherent": "OK",
        }
        sealed_index = {
            "pointers": [
                {
                    "lane": "headline",
                    "proof_pool_ref": "pool-a",
                    "proof_pool_digest": "digest-a",
                },
                {
                    "lane": "executive_summary",
                    "proof_pool_ref": "pool-a",
                    "proof_pool_digest": "digest-a",
                },
            ]
        }
        return fingerprint, sealed_index

    def _fake_preflight(**kwargs):
        return [SimpleNamespace(pass_=True)]

    monkeypatch.setattr(policy_mod, "build_fingerprint_from_rollup", _fake_build_fingerprint_from_rollup)
    monkeypatch.setattr(policy_mod, "run_aggregation_preflight", _fake_preflight)


def test_mixed_date_pins_are_not_accepted_for_structural_assembly(monkeypatch) -> None:
    _patch_policy_inputs(monkeypatch, same_date_prefix_coherent=False)

    policy = policy_mod.evaluate_coherent_rollup_policy(
        repo=Path("C:/tmp/repo"),
        rollup_blob={"coherent_aggregation_pin": True},
        base_resume_digest="base-digest",
    )

    assert policy["same_run_policy"]["acceptable_for_structural_assembly"] is False
    assert policy["structural_assembly_eligible"] is False
    assert "not accepted even under coherent_aggregation_pin" in policy["same_run_policy"][
        "coherent_rollup_policy_reason"
    ]


def test_same_session_pins_still_allow_structural_assembly(monkeypatch) -> None:
    _patch_policy_inputs(monkeypatch, same_date_prefix_coherent=True)

    policy = policy_mod.evaluate_coherent_rollup_policy(
        repo=Path("C:/tmp/repo"),
        rollup_blob={},
        base_resume_digest="base-digest",
    )

    assert policy["same_run_policy"]["acceptable_for_structural_assembly"] is True
    assert policy["structural_assembly_eligible"] is True
