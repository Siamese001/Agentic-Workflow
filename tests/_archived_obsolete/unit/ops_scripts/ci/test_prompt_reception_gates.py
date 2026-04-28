"""W5 tests for prompt-reception CI gates."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ops_scripts.ci.check_exemplar_coverage import validate_config
from ops_scripts.ci.check_prompt_reception_v2 import validate_gateway_wiring


REPO_ROOT = Path(__file__).resolve().parents[4]


class TestExemplarCoverageGate:
    def test_repo_default_config_valid(self) -> None:
        """The shipped exemplar_eligibility.yaml must be valid."""
        cfg = REPO_ROOT / "config" / "prompt_governance" / "exemplar_eligibility.yaml"
        ok, errors = validate_config(cfg)
        assert ok, f"default config failed: {errors}"

    def test_minimum_below_three_rejected(self, tmp_path: Path) -> None:
        cfg = tmp_path / "bad.yaml"
        cfg.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "eligible_task_classes": [
                        {
                            "task_class": "x",
                            "reason": "r",
                            "owner": "o",
                            "minimum_examples": 2,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        ok, errors = validate_config(cfg)
        assert not ok
        assert any("minimum_examples" in e for e in errors)

    def test_duplicate_task_class_rejected(self, tmp_path: Path) -> None:
        cfg = tmp_path / "dup.yaml"
        cfg.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "eligible_task_classes": [
                        {"task_class": "x", "reason": "r", "owner": "o"},
                        {"task_class": "x", "reason": "r2", "owner": "o2"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        ok, errors = validate_config(cfg)
        assert not ok
        assert any("duplicate" in e for e in errors)

    def test_missing_required_fields(self, tmp_path: Path) -> None:
        cfg = tmp_path / "missing.yaml"
        cfg.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "eligible_task_classes": [{"task_class": "x"}],
                }
            ),
            encoding="utf-8",
        )
        ok, errors = validate_config(cfg)
        assert not ok
        assert any("reason" in e for e in errors)
        assert any("owner" in e for e in errors)

    def test_wrong_schema_version(self, tmp_path: Path) -> None:
        cfg = tmp_path / "ver.yaml"
        cfg.write_text(
            yaml.safe_dump({"schema_version": 99, "eligible_task_classes": []}),
            encoding="utf-8",
        )
        ok, errors = validate_config(cfg)
        assert not ok
        assert any("schema_version" in e for e in errors)

    def test_missing_file(self, tmp_path: Path) -> None:
        ok, errors = validate_config(tmp_path / "nope.yaml")
        assert not ok
        assert any("load failed" in e for e in errors)


class TestReceptionV2Gate:
    def test_repo_gateway_wiring_intact(self) -> None:
        """Live gateway file must pass the wiring gate."""
        gateway = REPO_ROOT / "agentic_core" / "L2_execution" / "enforcement" / "SovereignLLMGateway.py"
        ok, errors = validate_gateway_wiring(gateway)
        assert ok, f"gateway wiring gate failed: {errors}"

    def test_unwired_stub_rejected(self, tmp_path: Path) -> None:
        stub = tmp_path / "SovereignLLMGateway.py"
        stub.write_text(
            "class SovereignLLMGateway:\n"
            "    def generate(self, artifact): return 'ok'\n"
            "    def generate_with_reasoning(self, artifact): return 'ok'\n",
            encoding="utf-8",
        )
        ok, errors = validate_gateway_wiring(stub)
        assert not ok
        assert any("missing import" in e for e in errors)
        assert any("_resolve_provider_payload" in e for e in errors)

    def test_missing_gateway_file(self, tmp_path: Path) -> None:
        ok, errors = validate_gateway_wiring(tmp_path / "nope.py")
        assert not ok
        assert any("not found" in e for e in errors)
