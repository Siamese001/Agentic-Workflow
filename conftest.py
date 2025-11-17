"""Shared pytest fixtures for canonical tests in tests_flat and tests.

Tests in ``tests_flat`` are considered canonical for v10_9; the legacy ``tests``
directory is kept for parity and shares these fixtures.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

# Ensure repository root is importable regardless of invocation path.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core_v10_7.config import ConfigV10_7, load_config
from core_v10_7.context import WorkflowContext


@pytest.fixture(scope="session")
def testdata_dir() -> Path:
    return ROOT / "tests_flat" / "testdata"


@pytest.fixture(scope="session")
def sample_job_input(testdata_dir: Path) -> Dict[str, Any]:
    with open(testdata_dir / "job_input_sample.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_master_resume(testdata_dir: Path) -> Dict[str, Any]:
    with open(testdata_dir / "master_resume_sample.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def config_v10_7() -> ConfigV10_7:
    master_path = ROOT / "master_config_v10_7.json"
    if master_path.exists():
        with open(master_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    return load_config(data)


@pytest.fixture()
def workflow_context(config_v10_7: ConfigV10_7) -> WorkflowContext:
    return WorkflowContext(config_v10_7)


@pytest.fixture()
def create_workflow_context(config_v10_7: ConfigV10_7):
    def _builder(**overrides: Any) -> WorkflowContext:
        return WorkflowContext(config_v10_7, **overrides)

    return _builder
