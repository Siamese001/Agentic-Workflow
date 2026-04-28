"""ExitDisposition must exist whenever a sealed L2 artifact does."""

from __future__ import annotations

from pathlib import Path


def test_exit_disposition_present_when_sealed(proof_dir: Path) -> None:
    sealed = proof_dir / "contracts" / "l2_sealed_artifact.json"
    exit_d = proof_dir / "contracts" / "exit_disposition.json"
    if sealed.exists():
        assert exit_d.exists(), (
            "sealed artifact present but exit_disposition.json missing — "
            "would FAIL_OUTPUT_WITHOUT_EXIT"
        )
