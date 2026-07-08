#!/usr/bin/env python3
"""CI guard for apps_rg L5 packet and egress runtime wiring."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_TOKENS = {
    "apps_rg/runtime/spine/governed_l2_exit_compose.py": (
        "build_l5_certification_packet",
        "attach_l5_packet_to_sealed",
    ),
    "apps_rg/runtime/bindings/exit_binding.py": (
        "_evaluate_l5_certification_gate",
        "l5_certification_packet_digest",
        "l5_certification_status",
    ),
    "apps_rg/runtime/bindings/l2_envelope_adapter.py": (
        "receipt_from_provider_exchange",
        "l5_egress_receipts",
    ),
}
L5_PACKET_TOKENS = (
    "l5_certification_packet",
    "l5_packet",
    "L5CertificationPacket",
)


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    for rel, tokens in REQUIRED_TOKENS.items():
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"MISSING_FILE {rel}")
            continue
        source = _read(rel)
        for token in tokens:
            if token not in source:
                errors.append(f"MISSING_TOKEN {rel} expected {token!r}")

    for path in sorted((REPO_ROOT / "apps_rg").rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(source.splitlines(), start=1):
            if "gate_verdict_refs" in line and any(token in line for token in L5_PACKET_TOKENS):
                errors.append(f"L5_IN_GATE_VERDICTS {rel}:{lineno}")

    print(f"[APPS-RG-L5-WIRING] checked {len(REQUIRED_TOKENS)} runtime files, {len(errors)} issue(s)")
    if errors:
        for error in errors:
            print(f"  ERROR  {error}")
        return 1
    print("[APPS-RG-L5-WIRING] runtime L5 packet wiring gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
