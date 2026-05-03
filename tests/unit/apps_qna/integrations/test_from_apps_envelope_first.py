"""Consumer-side envelope-first loading with regex fallback (Wave 4).

Plan: apps-cross-app-precursors-c94c71.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import pytest
import yaml

from apps_exec.outputs.envelope_emitter import emit as emit_exec
from apps_qna.integrations.from_apps_exec import load_executive_close_patterns
from apps_qna.integrations.from_apps_research import load_apps_research
from apps_qna.integrations.from_apps_rg import load_experience_yaml
from apps_qna.integrations.from_apps_shared import load_master_resume
from apps_research.outputs.envelope_emitter import emit as emit_research
from apps_rg.outputs.envelope_emitter import emit as emit_rg
from apps_shared.outputs.experience_library_emitter import emit as emit_shared


def _write_master(tmp_path: Path) -> Path:
    p = tmp_path / "master_resume.json"
    p.write_text(
        json.dumps(
            {
                "executive_summary": "s",
                "professional_experience": [
                    {
                        "title": "VP",
                        "bullet_pool": [
                            {"label": "Lead", "text": "Led Y.", "tags": ["t"]},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return p


def test_shared_envelope_first(tmp_path):
    master = _write_master(tmp_path)
    emit_shared(source_path=master, trace_id="tt")
    # No warning when envelope is present.
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        lib = load_master_resume(master)
    assert len(lib.points) == 1
    assert lib.points[0].technical_depth_tags == ["t"]


def test_shared_regex_fallback_warns(tmp_path):
    master = _write_master(tmp_path)
    # no envelope emitted
    with pytest.warns(DeprecationWarning, match="Envelope missing"):
        lib = load_master_resume(master)
    assert len(lib.points) == 1


def _write_research(tmp_path: Path) -> Path:
    rdir = tmp_path / "research"
    rdir.mkdir()
    brief = rdir / "research_brief_abc123.md"
    brief.write_text(
        "## Executive Summary\n\nHello.\n\n"
        "## Key Findings\n\n- a\n- b\n\n"
        "## Strategic Implications\n\n- t1\n",
        encoding="utf-8",
    )
    return rdir


def test_research_envelope_first(tmp_path):
    rdir = _write_research(tmp_path)
    emit_research(trace_id="abc123", research_dir=rdir)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        ri = load_apps_research(trace_id="abc123", research_dir=rdir)
    assert ri.role_areas_of_focus == ["a", "b"]
    assert ri.industry_trends == ["t1"]


def test_research_regex_fallback_warns(tmp_path):
    rdir = _write_research(tmp_path)
    with pytest.warns(DeprecationWarning, match="Envelope missing"):
        ri = load_apps_research(trace_id="abc123", research_dir=rdir)
    assert ri.role_areas_of_focus == ["a", "b"]


def _write_exec_brief(tmp_path: Path) -> Path:
    edir = tmp_path / "exec"
    edir.mkdir()
    brief = edir / "exec_brief_role_deadbeef.md"
    brief.write_text(
        "## Thesis\n\nT.\n\n## Patterns\n\n- pattern A\n- pattern B\n",
        encoding="utf-8",
    )
    return brief


def test_exec_envelope_first(tmp_path):
    brief = _write_exec_brief(tmp_path)
    emit_exec(brief_path=brief)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        patterns = load_executive_close_patterns(brief_path=brief)
    assert "pattern A" in patterns


def test_exec_regex_fallback_warns(tmp_path):
    brief = _write_exec_brief(tmp_path)
    with pytest.warns(DeprecationWarning, match="Envelope missing"):
        patterns = load_executive_close_patterns(brief_path=brief)
    assert "pattern A" in patterns


def _write_bank(tmp_path: Path) -> Path:
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
    return bank


def test_rg_envelope_first(tmp_path):
    bank = _write_bank(tmp_path)
    master = tmp_path / "m.json"
    master.write_text("{}", encoding="utf-8")
    emit_rg(bank_path=bank, master_resume_path=master, trace_id="tt")
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        lib = load_experience_yaml(bank)
    assert len(lib.points) == 1


def test_rg_regex_fallback_warns(tmp_path):
    bank = _write_bank(tmp_path)
    with pytest.warns(DeprecationWarning, match="Envelope missing"):
        lib = load_experience_yaml(bank)
    assert len(lib.points) == 1
