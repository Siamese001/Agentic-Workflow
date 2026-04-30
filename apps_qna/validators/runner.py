"""Linter runner — invokes all 6 validators, aggregates results."""

from __future__ import annotations

from apps_qna.config.route_registry import RouteRegistry, load_route_registry
from apps_qna.router.pack_loader import LoadedPack, load_pack
from apps_qna.validators.context_budget import (
    check_max_context,
    check_specialist_count,
)
from apps_qna.validators.header_consistency import check_header_consistency
from apps_qna.validators.route_coverage import check_no_orphan_cards
from apps_qna.validators.route_purity import (
    check_route_coverage,
    check_route_purity,
)
from apps_qna.validators.token_budget import check_token_budget
from apps_qna.validators.types import LintResult
from pathlib import Path

# Order matters for reporting determinism, not for correctness.
_VALIDATORS = (
    ("LINT-1 route purity", check_route_purity),
    ("LINT-2 specialist count", check_specialist_count),
    ("LINT-3 max-context", check_max_context),
    ("LINT-4 route coverage", check_route_coverage),
    ("LINT-5 no orphan cards", check_no_orphan_cards),
    ("LINT-6 header consistency", check_header_consistency),
    ("LINT-7 token budget", check_token_budget),
)


def run_all_validators(
    pack: LoadedPack | Path,
    registry: RouteRegistry | None = None,
) -> LintResult:
    """Run all 6 validators and return the aggregated result.

    Args:
        pack: A LoadedPack OR a Path to a pack directory (will be loaded).
        registry: Optional override RouteRegistry. Defaults to the bundled
            `apps_qna/config/route_registry.yaml`.

    Returns:
        Aggregated LintResult. `result.ok` is True iff no errors.
    """
    if isinstance(pack, Path):
        pack = load_pack(pack)
    registry = registry or load_route_registry()

    aggregate = LintResult(errors=[])
    for _name, validator in _VALIDATORS:
        aggregate = aggregate.merge(validator(pack, registry))
    return aggregate
