from __future__ import annotations

from pathlib import Path

from apps_eval.adapters.apps_lic import run_apps_lic_live


def test_apps_lic_live_adapter_forwards_redesign_inputs(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_build_cli_ingress_raw(**kwargs: object) -> dict[str, object]:
        captured["build_kwargs"] = dict(kwargs)
        return {"raw": "ingress"}

    def fake_run_canonical_apps_lic_spine(raw_ingress: dict[str, object], artifact_dir: Path) -> dict[str, str]:
        captured["raw_ingress"] = dict(raw_ingress)
        captured["artifact_dir"] = artifact_dir
        return {
            "x3_code": "X3D_ALLOW_FINISH",
            "message": "ok",
            "rationale": "ok",
            "compliance_notes": "ok",
        }

    import apps_lic.runtime.dispatch.canonical_dispatch as dispatch_module

    monkeypatch.setattr(dispatch_module, "build_cli_ingress_raw", fake_build_cli_ingress_raw)
    monkeypatch.setattr(dispatch_module, "run_canonical_apps_lic_spine", fake_run_canonical_apps_lic_spine)

    snapshot = run_apps_lic_live(
        "redesign_case",
        {
            "channel": "linkedin",
            "recipient_class": "recruiter",
            "outreach_mode": "cold",
            "manual_brief": "JD-anchored recruiter outreach",
            "lead_profile": {
                "name": "Jordan",
                "role_context": "hiring senior AI platform leaders",
            },
            "campaign_objective": "open a recruiter conversation",
            "connection_status": "NOT_CONNECTED",
            "premium_available": False,
            "allow_research": True,
            "audience_segment": "recruiting",
            "message_type_hint": "role_specific",
            "message_modifiers": {
                "uses_jd": True,
                "application_status_claimed": True,
                "uses_sensitive_constraints": False,
            },
            "application_status": "applied",
            "desired_next_step": "short screen",
            "governed_opportunity_facts": [
                {
                    "namespace": "apps_lic_jd_facts",
                    "fact_id": "jd_1",
                    "source_snapshot_id": "jd:example",
                    "fact_text": "Role requires senior AI platform leadership.",
                }
            ],
            "c0_required_namespaces": ["apps_lic_jd_facts"],
        },
        tmp_path / "artifacts",
    )

    build_kwargs = captured["build_kwargs"]
    assert isinstance(build_kwargs, dict)
    assert build_kwargs["recipient_class"] == "recruiter"
    assert build_kwargs["channel"] == "linkedin"
    assert build_kwargs["outreach_mode"] == "cold"
    assert build_kwargs["manual_brief"] == "JD-anchored recruiter outreach"
    assert build_kwargs["allow_research"] is True
    assert build_kwargs["connection_status"] == "NOT_CONNECTED"
    assert build_kwargs["premium_available"] is False
    assert build_kwargs["audience_segment"] == "recruiting"
    assert build_kwargs["message_type_hint"] == "role_specific"
    assert build_kwargs["message_modifiers"] == {
        "uses_jd": True,
        "application_status_claimed": True,
        "uses_sensitive_constraints": False,
    }
    assert build_kwargs["application_status"] == "applied"
    assert build_kwargs["desired_next_step"] == "short screen"
    assert build_kwargs["c0_required_namespaces"] == ["apps_lic_jd_facts"]
    assert build_kwargs["governed_opportunity_facts"] == [
        {
            "namespace": "apps_lic_jd_facts",
            "fact_id": "jd_1",
            "source_snapshot_id": "jd:example",
            "fact_text": "Role requires senior AI platform leadership.",
        }
    ]

    assert captured["raw_ingress"] == {"raw": "ingress"}
    assert captured["artifact_dir"] == tmp_path / "artifacts"
    assert snapshot.app_id == "apps_lic"
    assert snapshot.scenario_id == "redesign_case"
    assert snapshot.x3_disposition == "X3D_ALLOW_FINISH"
    assert snapshot.output["result"]["message"] == "ok"
    assert snapshot.provenance["entrypoints"] == [
        "apps_lic.runtime.dispatch.canonical_dispatch:build_cli_ingress_raw",
        "apps_lic.runtime.dispatch.canonical_dispatch:run_canonical_apps_lic_spine",
    ]
