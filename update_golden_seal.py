#!/usr/bin/env python3
"""Update the golden seal with current core integrity hash."""

from agentic_core.domain.CoreIntegrityVerifier import CoreIntegrityVerifier

if __name__ == "__main__":
    CoreIntegrityVerifier.update_golden_seal()
    print("✅ Golden seal updated successfully")
