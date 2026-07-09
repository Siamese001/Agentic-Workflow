"""``apps_rg_parse`` preserves JD / resume / brief fields and enriches resume inline text."""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_core.runtime.contracts.apps_rg_ingress_payload import RequestEnvelope
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse


def test_parse_preserves_jd_resume_brief_refs_and_enriches_resume_text(tmp_path: Path) -> None:
    jd = tmp_path / "jd.txt"
    jd.write_text("JD from file.\n", encoding="utf-8")
    logging.info("C3 write receipt: apps_rg dispatch text fixtures written")
    resume = tmp_path / "cv.json"
    resume.write_text('{"facts":{"employment":[]}}', encoding="utf-8")
    brief = tmp_path / "brief.txt"
    brief.write_text("Briefing.\n", encoding="utf-8")

    env = apps_rg_parse(
        {
            "target_company": "Co",
            "target_role": "Role",
            "job_description_ref": str(jd),
            "job_description_text": "inline jd",
            "source_resume_ref": str(resume),
            "source_resume_text": "",
            "briefing_artifact_ref": str(brief),
            "manual_brief_path": str(brief),
            "l5_certification_ref": "test:valid:w6",
        }
    )
    assert isinstance(env, RequestEnvelope)
    p = env.payload
    assert p.job_description_ref == str(jd)
    assert p.job_description_text == "inline jd"
    assert p.source_resume_ref == str(resume)
    assert p.source_resume_text.strip()
    assert p.briefing_artifact_ref == str(brief)

    vr = u0_validate_apps_rg(env)
    ap = dict(vr.app_payload)
    assert ap.get("job_description_ref") == str(jd)
    assert ap.get("job_description_text") == "inline jd"
    assert ap.get("source_resume_ref") == str(resume)
    assert ap.get("source_resume_text") == p.source_resume_text
    assert ap.get("briefing_artifact_ref") == str(brief)
    assert ap.get("manual_brief_path") == str(brief)
