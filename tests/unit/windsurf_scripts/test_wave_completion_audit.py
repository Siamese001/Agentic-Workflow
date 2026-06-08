"""Unit tests for .claude/governance/scripts/post_agent_wave_completion_audit.py.

RCA: rca-wave-marker-emission-gap-c7d3f1 W4.P1.

Key invariants verified:
- GAP-1 fix: audit fires WITHOUT requiring wave_execution_state.py start
  (i.e. _has_active_plan guard is gone — main() must not import or call it)
- GAP-2 fix: hook is registered in the active post-agent dispatcher
- GAP-3 fix: EDIT_PATTERNS detects the actual Windsurf tool-call shapes
- Advisory fires when write_count >= 3 and no markers
- Advisory does NOT fire when write_count < 3
- Advisory does NOT fire when markers present
- Bypass env var suppresses advisory
"""
from __future__ import annotations

import importlib
import io
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_wave_completion_audit.py"
DISPATCH_PATH = REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_dispatch.py"


def _load_module():
    sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance" / "scripts"))
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(
        "post_agent_wave_completion_audit", HOOK_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    key = "post_agent_wave_completion_audit"
    if key in sys.modules:
        del sys.modules[key]
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_dispatch_module():
    spec = importlib.util.spec_from_file_location("post_agent_dispatch", DISPATCH_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hook():
    return _load_module()


# ---------------------------------------------------------------------------
# GAP-1: _has_active_plan() must NOT be called in main()
# ---------------------------------------------------------------------------

class TestGap1GuardRemoved:
    def test_no_has_active_plan_function(self, hook):
        """_has_active_plan was removed; main() must not gate on plan state."""
        assert not hasattr(hook, "_has_active_plan"), (
            "_has_active_plan() still exists in the module — GAP-1 not fully fixed"
        )

    def test_advisory_fires_without_active_plan_state(self, hook, tmp_path, capsys):
        """Advisory fires even when wave_execution_state.py start was never called."""
        # Simulate a response with 3+ file writes but no wave markers
        payload = json.dumps({
            "response_text": (
                '<invoke name="edit">\n'
                '<invoke name="edit">\n'
                '<invoke name="edit">\n'
            )
        })
        log_path = tmp_path / "wave_completion_audit.jsonl"
        with (
            patch.object(hook, "LOG_PATH", log_path),
            patch("sys.stdin", io.StringIO(payload)),
            patch.dict(os.environ, {}, clear=False),
        ):
            # Remove bypass if set
            os.environ.pop("WAVE_COMPLETION_AUDIT_BYPASS", None)
            rc = hook.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "ADVISORY" in captured.err, "Advisory must fire regardless of plan state"


# ---------------------------------------------------------------------------
# GAP-2: active dispatcher must register audit hook
# ---------------------------------------------------------------------------

class TestGap2ActiveDispatch:
    def test_registered_in_post_agent_dispatch_chain(self):
        dispatch = _load_dispatch_module()
        assert "post_agent_wave_completion_audit.py" in dispatch.LEGACY_SCRIPTS


# ---------------------------------------------------------------------------
# GAP-3: EDIT_PATTERNS detects Windsurf tool-call shapes
# ---------------------------------------------------------------------------

class TestGap3EditPatterns:
    def test_detects_invoke_edit_tag(self, hook):
        text = '<invoke name="edit"><file_path>foo.py</file_path></invoke>'
        count = hook._count_file_writes(text)
        assert count >= 1

    def test_detects_invoke_write_to_file_tag(self, hook):
        text = '<invoke name="write_to_file"><TargetFile>bar.py</TargetFile></invoke>'
        count = hook._count_file_writes(text)
        assert count >= 1

    def test_detects_file_path_xml(self, hook):
        text = "<file_path>/path/to/file.py</file_path>"
        count = hook._count_file_writes(text)
        assert count >= 1

    def test_detects_target_file_json(self, hook):
        text = '"TargetFile": "/path/to/some/file.py"'
        count = hook._count_file_writes(text)
        assert count >= 1

    def test_detects_file_path_json(self, hook):
        text = '"file_path": "/src/module.py"'
        count = hook._count_file_writes(text)
        assert count >= 1

    def test_three_edits_counted(self, hook):
        text = (
            '<invoke name="edit">\n'
            '<invoke name="edit">\n'
            '<invoke name="edit">\n'
        )
        count = hook._count_file_writes(text)
        assert count >= 3


# ---------------------------------------------------------------------------
# Advisory logic
# ---------------------------------------------------------------------------

class TestAdvisoryLogic:
    def _run(self, hook, tmp_path, response_text: str, env_overrides: dict | None = None):
        payload = json.dumps({"response_text": response_text})
        log_path = tmp_path / "wave_completion_audit.jsonl"
        env = dict(os.environ)
        env.pop("WAVE_COMPLETION_AUDIT_BYPASS", None)
        if env_overrides:
            env.update(env_overrides)
        with (
            patch.object(hook, "LOG_PATH", log_path),
            patch("sys.stdin", io.StringIO(payload)),
            patch.dict(os.environ, env, clear=True),
        ):
            import io as _io
            import sys as _sys
            old_stderr = _sys.stderr
            _sys.stderr = _io.StringIO()
            rc = hook.main()
            stderr_out = _sys.stderr.getvalue()
            _sys.stderr = old_stderr
        return rc, stderr_out

    def test_advisory_fires_on_3_writes_no_markers(self, hook, tmp_path):
        text = '<invoke name="edit">\n' * 3
        rc, err = self._run(hook, tmp_path, text)
        assert rc == 0
        assert "ADVISORY" in err

    def test_no_advisory_on_2_writes(self, hook, tmp_path):
        text = '<invoke name="edit">\n' * 2
        rc, err = self._run(hook, tmp_path, text)
        assert rc == 0
        assert "ADVISORY" not in err

    def test_no_advisory_when_markers_present(self, hook, tmp_path):
        text = (
            '<invoke name="edit">\n' * 4 +
            "WAVE_COMPLETE: plan=my-plan-abc123 wave=1\n"
        )
        rc, err = self._run(hook, tmp_path, text)
        assert rc == 0
        assert "ADVISORY" not in err

    def test_wave_start_marker_also_suppresses(self, hook, tmp_path):
        text = (
            '<invoke name="edit">\n' * 4 +
            "WAVE_START: plan=my-plan-abc123 wave=2\n"
        )
        rc, err = self._run(hook, tmp_path, text)
        assert rc == 0
        assert "ADVISORY" not in err

    def test_bypass_suppresses_advisory(self, hook, tmp_path):
        text = '<invoke name="edit">\n' * 5
        rc, err = self._run(hook, tmp_path, text, {"WAVE_COMPLETION_AUDIT_BYPASS": "1"})
        assert rc == 0
        assert "ADVISORY" not in err

    def test_empty_response_no_advisory(self, hook, tmp_path):
        rc, err = self._run(hook, tmp_path, "")
        assert rc == 0
        assert "ADVISORY" not in err


# ---------------------------------------------------------------------------
# _has_wave_markers helper
# ---------------------------------------------------------------------------

class TestHasWaveMarkers:
    def test_detects_wave_complete(self, hook):
        assert hook._has_wave_markers("WAVE_COMPLETE: plan=foo wave=1")

    def test_detects_wave_start(self, hook):
        assert hook._has_wave_markers("WAVE_START: plan=foo wave=2")

    def test_ignores_inline_mention(self, hook):
        assert not hook._has_wave_markers("emit WAVE_COMPLETE: in prose — not a marker")

    def test_multiline_detects_marker_line(self, hook):
        text = "some text\nWAVE_COMPLETE: plan=x wave=1\nmore text"
        assert hook._has_wave_markers(text)
