"""Lint result types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LintError:
    """One linter violation."""

    code: str  # LINT-1, LINT-2, ...
    message: str
    where: str = ""  # filename or route id, optional


@dataclass(frozen=True)
class LintResult:
    """Aggregate result of running all validators on a pack."""

    errors: list[LintError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "LintResult") -> "LintResult":
        return LintResult(errors=[*self.errors, *other.errors])
