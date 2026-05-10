"""CI Gate: AG-8-FU2 — apps_lic must use shared build_x3_packet path.

Checks:
  FU2-1  build_x3_packet is imported in apps_lic_exit_binding.py
  FU2-2  build_x3_packet is called (non-comment code) in exit_finalize_apps_lic
  FU2-3  exit_finalize_apps_lic does not directly construct X3Disposition
  FU2-4  ExitReviewPacket is constructed with l5_certification_refs populated
  FU2-5  No direct L4/ChromaDB write in exit binding
  FU2-6  No embedding generation in exit binding
  FU2-7  _x3_packet_to_disposition bridge helper exists
  FU2-8  l5_certification_ref is taken from x3_pkt not hardcoded in bridge

Bypass: AG8_FU2_PATH_BYPASS=1
Fail-closed: AG8_FU2_PATH_FAIL_CLOSED=1
"""
from __future__ import annotations

import ast
import inspect
import os
import re
import sys
import textwrap
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).parents[2]


def _load_source(rel: str) -> str:
    path = _repo_root() / rel
    return path.read_text(encoding="utf-8")


def _code_only(src: str) -> str:
    lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------

def check_fu2_1_build_x3_packet_imported(src: str) -> list[str]:
    violations = []
    if "from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3_packet" not in src:
        violations.append(
            "FU2-1: build_x3_packet not imported from shared x3_dispositions in apps_lic_exit_binding.py"
        )
    return violations


def check_fu2_2_build_x3_packet_called(src: str) -> list[str]:
    violations = []
    code = _code_only(src)
    if "build_x3_packet(" not in code:
        violations.append(
            "FU2-2: build_x3_packet() is not called in apps_lic_exit_binding.py non-comment code"
        )
    return violations


def check_fu2_3_no_direct_x3disposition_in_finalize(src: str) -> list[str]:
    """exit_finalize_apps_lic must not directly construct X3Disposition.

    The bridge helper _x3_packet_to_disposition IS allowed to use X3Disposition(...)
    but the main finalize function must delegate via the bridge.
    """
    violations = []
    # Extract the exit_finalize_apps_lic function source
    import importlib
    try:
        mod = importlib.import_module("agentic_core.runtime.exit.apps_lic_exit_binding")
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        func_src = inspect.getsource(exit_finalize_apps_lic)
        if "X3Disposition(" in func_src:
            violations.append(
                "FU2-3: exit_finalize_apps_lic directly constructs X3Disposition — "
                "must delegate to _x3_packet_to_disposition bridge (AG-8-FU2)"
            )
    except Exception as exc:
        violations.append(f"FU2-3: could not import exit_finalize_apps_lic: {exc}")
    return violations


def check_fu2_4_l5_certification_refs_populated(src: str) -> list[str]:
    """_build_exit_review_packet must pass l5_certification_refs to ExitReviewPacket."""
    violations = []
    code = _code_only(src)
    if "l5_certification_refs=" not in code:
        violations.append(
            "FU2-4: l5_certification_refs not populated on ExitReviewPacket in apps_lic_exit_binding.py"
        )
    return violations


def check_fu2_5_no_direct_l4_write(src: str) -> list[str]:
    violations = []
    forbidden = ["chromadb", "chroma_client", ".upsert(", ".delete(", "L4_state"]
    for pattern in forbidden:
        if pattern in src:
            violations.append(f"FU2-5: Forbidden L4/ChromaDB pattern {pattern!r} in apps_lic_exit_binding.py")
    return violations


def check_fu2_6_no_embedding_generation(src: str) -> list[str]:
    violations = []
    forbidden = ["embed(", "sentence_transformers", "openai.Embedding", "embeddings.create", "model.encode("]
    for pattern in forbidden:
        if pattern in src:
            violations.append(f"FU2-6: Forbidden embedding pattern {pattern!r} in apps_lic_exit_binding.py")
    return violations


def check_fu2_7_bridge_helper_exists(src: str) -> list[str]:
    violations = []
    if "def _x3_packet_to_disposition(" not in src:
        violations.append(
            "FU2-7: _x3_packet_to_disposition bridge helper not found in apps_lic_exit_binding.py"
        )
    return violations


def check_fu2_8_cert_ref_from_x3_pkt(src: str) -> list[str]:
    """Bridge must use x3_pkt.l5_certification_ref, not hardcoded _CERT_REF."""
    violations = []
    try:
        import importlib
        mod = importlib.import_module("agentic_core.runtime.exit.apps_lic_exit_binding")
        from agentic_core.runtime.exit.apps_lic_exit_binding import _x3_packet_to_disposition
        bridge_src = inspect.getsource(_x3_packet_to_disposition)
        if "x3_pkt.l5_certification_ref" not in bridge_src:
            violations.append(
                "FU2-8: _x3_packet_to_disposition must use x3_pkt.l5_certification_ref "
                "(not hardcoded _CERT_REF) to thread cert ref from shared builder"
            )
    except Exception as exc:
        violations.append(f"FU2-8: could not inspect _x3_packet_to_disposition: {exc}")
    return violations


# ---------------------------------------------------------------------------

def run_all_checks() -> list[str]:
    src = _load_source("agentic_core/runtime/exit/apps_lic_exit_binding.py")
    all_violations: list[str] = []
    all_violations.extend(check_fu2_1_build_x3_packet_imported(src))
    all_violations.extend(check_fu2_2_build_x3_packet_called(src))
    all_violations.extend(check_fu2_3_no_direct_x3disposition_in_finalize(src))
    all_violations.extend(check_fu2_4_l5_certification_refs_populated(src))
    all_violations.extend(check_fu2_5_no_direct_l4_write(src))
    all_violations.extend(check_fu2_6_no_embedding_generation(src))
    all_violations.extend(check_fu2_7_bridge_helper_exists(src))
    all_violations.extend(check_fu2_8_cert_ref_from_x3_pkt(src))
    return all_violations


def main() -> int:
    bypass = os.environ.get("AG8_FU2_PATH_BYPASS", "").strip()
    if bypass == "1":
        print("WARNING: AG8_FU2_PATH_BYPASS=1 — skipping AG-8-FU2 shared-x3-path gate")
        return 0

    violations = run_all_checks()

    if not violations:
        print("AG-8-FU2 shared-x3-path gate: ALL CHECKS PASS")
        return 0

    fail_closed = os.environ.get("AG8_FU2_PATH_FAIL_CLOSED", "").strip()
    print(f"AG-8-FU2 shared-x3-path gate: {len(violations)} violation(s):")
    for v in violations:
        print(f"  - {v}")

    if fail_closed == "1":
        return 1

    print("(advisory — set AG8_FU2_PATH_FAIL_CLOSED=1 to make this fail-closed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
