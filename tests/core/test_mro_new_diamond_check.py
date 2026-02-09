"""Unit tests for mro_new_diamond_check.py (entry-level MRO prevention)."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ops_scripts.ci.mro_new_diamond_check import _diamond_key, main


class TestDiamondKey:
    def test_key_format(self):
        entry = {"file": "agentic_core/Foo.py", "class": "Bar"}
        assert _diamond_key(entry) == "agentic_core/Foo.py:Bar"


class TestExistingBaselinePasses:
    """Current baseline should pass — no new diamonds."""

    def test_current_baseline_passes(self):
        rc = main()
        assert rc == 0


FAKE_DIAMOND = {
    "file": "fake/NewFile.py",
    "line": 10,
    "class": "NewDiamond",
    "redundant_mixins": ["AtomicExecutionMixin"],
    "carriers": ["SovereignBaseAgent"],
}


class TestSyntheticNewDiamondFails:
    """A diamond NOT in baseline must cause FAIL."""

    def test_new_diamond_fails_exit_code(self, monkeypatch, capsys):
        """Mock scan_diamonds to return one diamond not in baseline."""
        monkeypatch.setattr(
            "ops_scripts.ci.mro_contract_check.scan_diamonds",
            lambda _root: [FAKE_DIAMOND],
        )
        monkeypatch.delenv("COMMIT_MESSAGE", raising=False)

        rc = main()
        assert rc == 1
        captured = capsys.readouterr()
        assert "FAIL" in captured.out
        assert "NewDiamond" in captured.out

    def test_bump_tag_without_baseline_update_fails(self, monkeypatch, capsys):
        """Bump tag present but new diamond not in baseline → still FAIL."""
        monkeypatch.setattr(
            "ops_scripts.ci.mro_contract_check.scan_diamonds",
            lambda _root: [FAKE_DIAMOND],
        )
        monkeypatch.setenv("COMMIT_MESSAGE", "MRO_BASELINE_BUMP:test reason")

        rc = main()
        assert rc == 1
        captured = capsys.readouterr()
        assert "not added to baseline" in captured.out

    def test_key_not_in_empty_baseline(self):
        """Verify key logic: fake diamond key not in empty set."""
        assert _diamond_key(FAKE_DIAMOND) not in set()
