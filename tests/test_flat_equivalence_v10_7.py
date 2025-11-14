"""Ensure the flattened test view stays synchronized with the source files."""
from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Iterable, List, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

FLAT_TO_SOURCES: Dict[str, List[str]] = {
    "tests_flat/test_architecture_flat_v10_7.py": [
        "tests/architecture/test_architecture_compliance_v10_7.py",
        "tests/design/test_design_validation_dag_v10_7.py",
        "tests/architecture/test_core_module_exports.py",
        "tests/architecture/test_config_v10_7.py",
    ],
    "tests_flat/test_contract_flat_v10_7.py": [
        "tests/contracts/test_contract_invariants_v10_7.py",
        "tests/contracts/test_contract_schemas_v10_7.py",
        "tests/test_baseline_schema_diff_v10_7.py",
    ],
    "tests_flat/test_rag_flat_v10_7.py": [
        "tests/rag/test_cache_rag_matrix_v10_7.py",
        "tests/rag/test_rag_invariants_v10_7.py",
    ],
    "tests_flat/test_qavalidation_flat_v10_7.py": [
        "tests/validation/test_semantic_and_qa_validation_v10_7.py",
    ],
    "tests_flat/test_routing_flat_v10_7.py": [
        "tests/routing/test_negative_routing_v10_7.py",
    ],
    "tests_flat/test_state_flat_v10_7.py": [
        "tests/state/test_state_evolution_v10_7.py",
    ],
    "tests_flat/test_perf_flat_v10_7.py": [
        "tests/integration/test_perf_latency_v10_7.py",
        "tests/integration/test_sla_latency_v10_7.py",
    ],
    "tests_flat/test_mcp_flat_v10_7.py": [
        "tests/mcp/test_mcp_context_v10_7.py",
        "tests/mcp/test_mcp_matrix_v10_7.py",
    ],
    "tests_flat/test_arbitration_flat_v10_7.py": [
        "tests/arbitration/test_arbitration_engine_v10_7.py",
        "tests/arbitration/test_arbitration_graph_wiring.py",
    ],
    "tests_flat/test_integration_flat_v10_7.py": [
        "tests/integration/test_integration_flow_v10_7.py",
        "tests/integration/test_end_to_end_paths_v10_7.py",
    ],
    "tests_flat/test_mocks_flat_v10_7.py": [
        "tests/mock_detection/test_mock_detection_v10_7.py",
        "tests/mock_detection/test_mock_sweeper_v10_7.py",
    ],
    "tests_flat/test_core_runtime_flat_v10_7.py": [
        "tests/core/test_core_runtime_v10_7.py",
    ],
}


def _flat_source_pairs() -> Iterable[Tuple[str, str]]:
    for flat_path, sources in FLAT_TO_SOURCES.items():
        for source in sources:
            yield flat_path, source


def _extract_block(flat_text: str, source_rel_path: str) -> str:
    begin = re.escape(f"# ----- BEGIN: {source_rel_path} -----")
    end = re.escape(f"# ----- END: {source_rel_path} -----")
    pattern = re.compile(begin + r"\n(?P<content>.*?)\n" + end, re.DOTALL)
    match = pattern.search(flat_text)
    if not match:
        raise AssertionError(
            f"Did not find block for {source_rel_path} inside flattened tests."
        )
    return match.group("content").strip("\n")


@pytest.mark.parametrize(
    ("flat_rel_path", "source_rel_path"),
    [pytest.param(flat, source, id=f"{flat}::{source}") for flat, source in _flat_source_pairs()],
)
def test_flat_view_matches_source_files(flat_rel_path: str, source_rel_path: str) -> None:
    """Every flattened block must mirror the exact source test file content."""
    flat_text = (REPO_ROOT / flat_rel_path).read_text(encoding="utf-8")
    source_text = (REPO_ROOT / source_rel_path).read_text(encoding="utf-8").strip("\n")
    flattened_block = _extract_block(flat_text, source_rel_path)
    assert (
        flattened_block == source_text
    ), f"Flattened block for {source_rel_path} diverges from source file."
