"""U0 must forward source_resume_ref without opening the referenced resume file."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg


def test_u0_validate_apps_rg_does_not_open_resume_file(tmp_path: Path) -> None:
    resume = tmp_path / "probe_resume.json"
    resume.write_text('{"U0":"must_not_read"}\n', encoding="utf-8")
    brief = tmp_path / "probe_briefing.txt"
    brief.write_text("U0 must not read this briefing body.\n", encoding="utf-8")

    payload = AppsRgIngressPayload(
        target_company="Co",
        target_role="Role",
        source_resume_text="",
        source_resume_ref=str(resume),
        job_description_text="jd body",
        manual_brief_path=str(brief),
        l5_certification_ref="test:valid:w6",
    )
    env = RequestEnvelope(payload=payload)

    opened: list[Path] = []
    orig_open = Path.open

    def _track_open(self: Path, *args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        try:
            if self.resolve() in {resume.resolve(), brief.resolve()}:
                opened.append(self)
        except OSError:
            pass
        return orig_open(self, *args, **kwargs)

    with patch.object(Path, "open", _track_open):
        vr = u0_validate_apps_rg(env)

    assert opened == [], "U0 must not open the source_resume_ref or briefing path"
    ap = dict(vr.app_payload)
    assert ap.get("source_resume_ref") == str(resume)
    assert ap.get("manual_brief_path") == str(brief)
