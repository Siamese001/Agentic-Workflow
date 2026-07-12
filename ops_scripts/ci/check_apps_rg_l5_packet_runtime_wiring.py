#!/usr/bin/env python3
"""CI guard for authenticated apps_rg L5 packet and UWG runtime wiring."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_TOKENS = {
    "apps_rg/runtime/l5/packet_builder.py": (
        "RUNTIME_OBJECT_BINDING_DOMAIN",
        "verify_l5_packet_against_runtime",
        "compute_l5_packet_verification_digest",
    ),
    "apps_rg/runtime/spine/governed_l2_exit_compose.py": (
        "build_l5_certification_packet",
        "attach_l5_packet_to_sealed",
        "prompt_artifact=prompt",
    ),
    "apps_rg/runtime/bindings/exit_binding.py": (
        "verify_l5_packet_against_runtime",
        "require_stored_verification=True",
        "l5_certification_verified",
    ),
    "apps_rg/runtime/bindings/l2_envelope_adapter.py": (
        "receipt_from_provider_exchange",
        "l5_egress_receipts",
    ),
    "apps_rg/cache/r1b_uwg_receipt_contract.py": (
        "l5_packet_not_verified_by_exit",
        "l5_verification_digest_mismatch",
        "compute_l5_packet_verification_digest",
    ),
}
L5_PACKET_TOKENS = (
    "l5_certification_packet",
    "l5_packet",
    "L5CertificationPacket",
)


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    for relative_path, tokens in REQUIRED_TOKENS.items():
        path = REPO_ROOT / relative_path
        if not path.is_file():
            errors.append(f"MISSING_FILE {relative_path}")
            continue
        source = _read(relative_path)
        for token in tokens:
            if token not in source:
                errors.append(f"MISSING_TOKEN {relative_path} expected {token!r}")

    for path in sorted((REPO_ROOT / "apps_rg").rglob("*.py")):
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(source.splitlines(), start=1):
            if "gate_verdict_refs" in line and any(
                token in line for token in L5_PACKET_TOKENS
            ):
                errors.append(f"L5_IN_GATE_VERDICTS {relative_path}:{line_number}")

    print(
        f"[APPS-RG-L5-WIRING] checked {len(REQUIRED_TOKENS)} runtime files, "
        f"{len(errors)} issue(s)"
    )
    if errors:
        for error in errors:
            print(f"  ERROR  {error}")
        return 1
    print("[APPS-RG-L5-WIRING] authenticated L5 packet wiring gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
