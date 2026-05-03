"""Producer-side emitter smoke tests (Wave 3).

Plan: apps-cross-app-precursors-c94c71.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from apps_exec.outputs.envelope_emitter import emit as emit_exec
from apps_research.outputs.envelope_emitter import emit as emit_research
from apps_rg.outputs.envelope_emitter import emit as emit_rg
from apps_shared.contracts.cross_app import (
    ExecutiveBriefEnvelope,
    ExperienceLibraryEnvelope,
    ResearchBriefEnvelope,
    ResumeBankEnvelope,
)
from apps_shared.outputs.experience_library_emitter import emit as emit_shared


def test_experience_library_emit_and_load(tmp_path):
    src = tmp_path / "master_resume.json"
    src.write_text(
        json.dumps(
            {
                "executive_summary": "summary",
                "engineering_and_platform_competencies": [
                    {"area": "Agentic", "skills": ["python"]}
                ],
                "professional_experience": [
                    {
                        "title": "VP",
                        "bullet_pool": [
                            "Legacy string bullet.",
                            {
                                "label": "Lead",
                                "text": "Led widget team.",
                                "tags": ["leadership"],
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "master_resume.envelope.json"
    written = emit_shared(source_path=src, trace_id="t1", out_path=out)
    assert written == out
    env = ExperienceLibraryEnvelope.load(out)
    assert env.payload.executive_summary == "summary"
    assert len(env.payload.bullets) == 2
    assert env.payload.bullets[1].tags == ["leadership"]


def test_research_brief_emit_and_load(tmp_path):
    rdir = tmp_path / "research"
    rdir.mkdir()
    brief = rdir / "research_brief_abc123.md"
    brief.write_text(
        "# Company Brief\n\n"
        "## Executive Summary\n\nAcme sells widgets.\n\n"
        "## Key Findings\n\n- focus A\n- focus B\n\n"
        "## Strategic Implications\n\n- trend 1\n",
        encoding="utf-8",
    )
    register = rdir / "source_register_abc123.json"
    register.write_text(
        json.dumps(
            [
                {
                    "summary": "Revenue up",
                    "claim_type": "direct_evidence",
                    "source_id": "SRC-1",
                    "section_id": "fin",
                }
            ]
        ),
        encoding="utf-8",
    )
    written = emit_research(trace_id="abc123", research_dir=rdir)
    assert written.name == "research_brief_abc123.envelope.json"
    env = ResearchBriefEnvelope.load(written)
    assert env.payload.company_brief == "Acme sells widgets."
    assert env.payload.role_areas_of_focus == ["focus A", "focus B"]
    assert env.payload.industry_trends == ["trend 1"]
    assert len(env.payload.source_register) == 1
    assert env.payload.source_register[0].source_id == "SRC-1"


def test_executive_brief_emit_and_load(tmp_path):
    edir = tmp_path / "exec"
    edir.mkdir()
    brief = edir / "exec_brief_role_abcd.md"
    brief.write_text(
        "# Exec\n\n"
        "## Thesis\n\nHire for platform leverage.\n\n"
        "## Close Patterns\n\n"
        "- Build agents that compound.\n"
        "- Protect the seams.\n",
        encoding="utf-8",
    )
    written = emit_exec(brief_path=brief)
    env = ExecutiveBriefEnvelope.load(written)
    assert "Build agents that compound." in env.payload.close_patterns
    assert "Hire for platform leverage." in env.payload.thesis_lines
    assert env.trace_id == "abcd"


def test_resume_bank_emit_and_load(tmp_path):
    bank = tmp_path / "resume_bank.yaml"
    bank.write_text(
        yaml.safe_dump(
            {
                "points": [{"title": "t", "one_liner": "o"}],
                "star_bank": {"stories": []},
                "rca_bank": [],
            }
        ),
        encoding="utf-8",
    )
    master = tmp_path / "master.json"
    master.write_text('{"x": 1}', encoding="utf-8")
    written = emit_rg(bank_path=bank, master_resume_path=master, trace_id="abc")
    env = ResumeBankEnvelope.load(written)
    assert env.payload.master_resume_source_sha256 != "0" * 64
    assert env.payload.points[0]["title"] == "t"
