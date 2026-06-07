"""Smoke test for plan l6-doctrinal-alignment-noninvasive-b9d3f5 W1.

Verifies the in-tree L6 layer markers landed on system_learning and its
27 subpackages with __init__.py. Markers are:

- system_learning.__layer__         == "L6"
- system_learning.__l6_surface__    == "active"
- system_learning.<sub>.__layer__   == "L6"  (for each subpackage)
- system_learning.<sub>.__l6_chapter__       canonical L6 chapter id
                                              (or "" for cross-cutting)

Failure here means W1 regressed. See docs/archive/windsurf/legacy-tree/plans/l6-doctrinal-alignment-noninvasive-b9d3f5.md.
"""
from __future__ import annotations

import importlib

import pytest

# Mirrors CHAPTER_MAP in docs/archive/windsurf/legacy-tree/scratch/_apply_l6_markers.py.
SUBPACKAGE_CHAPTERS: dict[str, str] = {
    "adg": "06.1",
    "adapters": "06.1",
    "arbitration": "06.5",
    "buses": "06.1",
    "config": "",
    "confidence": "06.5",
    "constraints": "06.2",
    "correlation": "06.3",
    "embedding": "06.5",
    "enforcement": "06.2",
    "engines": "06.3",
    "fingerprinting": "06.3",
    "golden": "06.4",
    "invariants": "06.2",
    "logs": "",
    "memory": "06.9",
    "meta_learning": "06.5",
    "ml_integration": "06.5",
    "monitoring": "06.8",
    "output": "06.6",
    "pipelines": "06.6",
    "policy": "06.2",
    "ports": "06.1",
    "provenance": "06.4",
    "raw": "06.1",
    "runtime": "",
    "rubrics": "06.3",
    "runtime_adg": "06.1",
    "scripts": "06.7",
    "snapshots": "06.8",
    "state": "06.7",
    "telemetry": "06.1",
    "stores": "06.9",
    "types": "",
    "validators": "06.2",
}

VALID_CHAPTERS = {
    "06.1",
    "06.2",
    "06.3",
    "06.4",
    "06.5",
    "06.6",
    "06.7",
    "06.8",
    "06.9",
    "",  # cross-cutting
}


def test_root_package_declares_l6_active_surface() -> None:
    sl = importlib.import_module("agentic_core.L6_system_learning")
    assert getattr(sl, "__layer__", None) == "L6"
    assert getattr(sl, "__l6_surface__", None) == "active"


@pytest.mark.parametrize("subname,expected_chapter", sorted(SUBPACKAGE_CHAPTERS.items()))
def test_subpackage_declares_l6_marker(subname: str, expected_chapter: str) -> None:
    mod = importlib.import_module(f"agentic_core.L6_system_learning.{subname}")
    assert getattr(mod, "__layer__", None) == "L6", (
        f"agentic_core.L6_system_learning.{subname} must declare __layer__ = 'L6'"
    )
    chapter = getattr(mod, "__l6_chapter__", None)
    assert chapter == expected_chapter, (
        f"agentic_core.L6_system_learning.{subname}.__l6_chapter__ expected {expected_chapter!r}, got {chapter!r}"
    )
    assert chapter in VALID_CHAPTERS, (
        f"agentic_core.L6_system_learning.{subname}.__l6_chapter__ {chapter!r} is not in canonical L6 chapter set"
    )
