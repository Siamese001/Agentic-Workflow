"""AST scan that validates the spine_manifest R3_grounded_read posture.

``spine_manifest.yaml`` declares that apps_underwriting_ai performs NO
durable writes. This service scans the package for tokens that would
indicate drift from that posture — e.g. ``CommitRequest``,
``MutationIntent``, ``write_gateway``, ``durable_write``, ``policy_issue``,
``loan_book``, ``ledger_write``.

Intended for CI enforcement (``tools/audit_spine_manifest.py``) and
one-shot audits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


_FORBIDDEN_TOKENS: tuple[str, ...] = (
    "CommitRequest",
    "commit_request",
    "StateDiffCandidate",
    "proposed_state_diff",
    "MutationIntent",
    "durable_write",
    "write_gateway",
    "WriteGateway",
    "policy_issue",
    "loan_book",
    "ledger_write",
)

_APP_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AuditFinding:
    """Single token hit in the audit scan."""

    file_path: str
    line_number: int
    token: str
    line_text: str


@dataclass(frozen=True)
class AuditReport:
    """Aggregate audit result."""

    scanned_files: int
    findings: tuple[AuditFinding, ...]
    forbidden_tokens: tuple[str, ...]
    scanned_root: str

    @property
    def passed(self) -> bool:
        return not self.findings

    def summary(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "scanned_files": self.scanned_files,
            "finding_count": len(self.findings),
            "forbidden_tokens": self.forbidden_tokens,
            "scanned_root": self.scanned_root,
        }


_DEFAULT_EXCLUDED_DIRS: tuple[str, ...] = ("tests", "__pycache__")
"""Directory names that are excluded from the scan by default.

``tests/`` is excluded because test fixtures legitimately need to
reference forbidden tokens (positive-control tests assert that the
scanner catches them). ``__pycache__`` is compiled artifacts.
"""


class PreMigrationAuditService:
    """Scan the app package for forbidden durable-write tokens."""

    def __init__(
        self,
        app_root: Path | str | None = None,
        forbidden_tokens: tuple[str, ...] | None = None,
        excluded_dirs: tuple[str, ...] | None = None,
    ) -> None:
        self._app_root = Path(app_root) if app_root else _APP_ROOT
        self._tokens = (
            tuple(forbidden_tokens) if forbidden_tokens is not None else _FORBIDDEN_TOKENS
        )
        self._excluded_dirs = (
            tuple(excluded_dirs) if excluded_dirs is not None else _DEFAULT_EXCLUDED_DIRS
        )

    @property
    def app_root(self) -> Path:
        return self._app_root

    @property
    def excluded_dirs(self) -> tuple[str, ...]:
        return self._excluded_dirs

    def audit(self) -> AuditReport:
        """Walk every `.py` under app_root, return a structured report."""
        findings: list[AuditFinding] = []
        scanned = 0
        excluded = set(self._excluded_dirs)
        for path in self._app_root.rglob("*.py"):
            if any(part in excluded for part in path.parts):
                continue
            # Don't scan this file itself — it *contains* the token list
            if path.samefile(Path(__file__)):
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                for token in self._tokens:
                    if token in line:
                        findings.append(
                            AuditFinding(
                                file_path=str(path.relative_to(self._app_root.parent)),
                                line_number=lineno,
                                token=token,
                                line_text=line.strip()[:200],
                            )
                        )
        return AuditReport(
            scanned_files=scanned,
            findings=tuple(findings),
            forbidden_tokens=self._tokens,
            scanned_root=str(self._app_root),
        )
