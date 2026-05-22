"""Shared helpers for PA core-law drift ratchet tests (W5)."""

from __future__ import annotations

import re

PRODUCT_SHAPE_HEADER = "PRODUCT_SHAPE (deterministic X2 authority"


def extract_i0_compiled_segment(content: str) -> str:
    """Text between SLOT: I0 and SLOT: C0 in a compiled section prompt."""
    i0_idx = content.find("<!-- SLOT: I0 -->")
    if i0_idx < 0:
        return ""
    i0_end = content.find("<!-- SLOT: C0 -->", i0_idx)
    if i0_end < 0:
        return content[i0_idx:]
    return content[i0_idx:i0_end]


def assert_single_product_shape_block(content: str, *, sample_gate_id: str) -> None:
    """Compiled prompt must carry exactly one PRODUCT_SHAPE appendix with lane gate IDs."""
    count = content.count(PRODUCT_SHAPE_HEADER)
    assert count == 1, f"expected exactly one PRODUCT_SHAPE block, found {count}"
    ps_idx = content.index(PRODUCT_SHAPE_HEADER)
    assert sample_gate_id in content[ps_idx:], (
        f"{sample_gate_id} must appear in PRODUCT_SHAPE block for this lane"
    )


def assert_i0_segment_has_no_x2_literals(
    i0_segment: str,
    pattern: re.Pattern[str],
    *,
    slot_label: str = "I0",
) -> None:
    hits = pattern.findall(i0_segment)
    assert not hits, f"{slot_label} must not enumerate X2 gate IDs (use PRODUCT_SHAPE): {hits}"
