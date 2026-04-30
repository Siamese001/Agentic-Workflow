"""Tests for the 6 routing-manifest invariant validators.

Each validator has at least one negative path (constructed by mutating the
synthetic-mini pack or the route registry) and one positive path (the smoke
build passes).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from apps_qna.builder.card_pack_builder import CardPackBuilder
from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.config.route_registry import (
    Route,
    RouteRegistry,
    load_route_registry,
)
from apps_qna.router.pack_loader import load_pack
from apps_qna.types.qna_types import Interview
from apps_qna.validators import run_all_validators
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

FIXTURES = Path(__file__).parent / "fixtures" / "synthetic_mini"
INTERVIEW_YAML = FIXTURES / "interview.yaml"


def _build_smoke_pack(tmp_path: Path) -> Path:
    """Build the synthetic-mini pack into tmp_path and return the dir."""
    output_dir = tmp_path / "pack"
    raw = yaml.safe_load(INTERVIEW_YAML.read_text(encoding="utf-8"))
    extra = raw.pop("extra_context", {}) or {}
    raw["build_metadata"]["output_dir"] = str(output_dir)
    raw["build_metadata"]["built_at"] = datetime.now(timezone.utc)
    interview = Interview.model_validate(raw)
    builder = CardPackBuilder(config=QnaBuildConfig(force=True))
    builder.build(interview, output_dir, extra)
    return output_dir


# ----------------- Positive: smoke pack passes all 6 -----------------


def test_valid_pack_passes_all_six_invariants(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    result = run_all_validators(pack_dir)
    assert result.ok, f"Unexpected errors: {result.errors}"


# ----------------- LINT-1: route purity -----------------


def test_lint1_route_purity_negative(tmp_path: Path) -> None:
    """Two routes claiming the same primary card → LINT-1 violation."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)

    real = load_route_registry()
    duplicated = real.routes[0].model_copy(update={"id": "duplicate_route"})
    bad_registry = RouteRegistry(
        version="v1",
        routes=[*real.routes, duplicated],
        tie_breaker_rules=real.tie_breaker_rules,
    )
    result = check_route_purity(pack, bad_registry)
    assert any(e.code == "LINT-1" for e in result.errors)


def test_lint1_route_purity_positive(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_route_purity(pack, load_route_registry())
    assert result.ok


# ----------------- LINT-2: specialist count -----------------


def test_lint2_specialist_count_negative(tmp_path: Path) -> None:
    """A route with >4 menu specialists → LINT-2 violation."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    real = load_route_registry()
    overloaded = real.routes[0].model_copy(
        update={
            "optional_specialists": ["A.md", "B.md", "C.md", "D.md", "E.md"],
        }
    )
    bad_registry = RouteRegistry(
        version="v1",
        routes=[overloaded, *real.routes[1:]],
        tie_breaker_rules=real.tie_breaker_rules,
    )
    result = check_specialist_count(pack, bad_registry)
    assert any(e.code == "LINT-2" for e in result.errors)


def test_lint2_specialist_count_positive(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_specialist_count(pack, load_route_registry())
    assert result.ok


# ----------------- LINT-3: max-context -----------------


def test_lint3_max_context_negative(tmp_path: Path) -> None:
    """Total menu > 5 → LINT-3 violation."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    real = load_route_registry()
    overloaded = real.routes[0].model_copy(
        update={
            "optional_specialists": ["A.md", "B.md", "C.md", "D.md", "E.md", "F.md"],
        }
    )
    bad_registry = RouteRegistry(
        version="v1",
        routes=[overloaded, *real.routes[1:]],
        tie_breaker_rules=real.tie_breaker_rules,
    )
    result = check_max_context(pack, bad_registry)
    assert any(e.code == "LINT-3" for e in result.errors)


def test_lint3_max_context_positive(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_max_context(pack, load_route_registry())
    assert result.ok


# ----------------- LINT-4: route coverage -----------------


def test_lint4_route_coverage_negative(tmp_path: Path) -> None:
    """A route whose primary card is missing on disk → LINT-4 violation."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    real = load_route_registry()
    bad_route = real.routes[0].model_copy(
        update={"primary_card": "99_NONEXISTENT.md"}
    )
    bad_registry = RouteRegistry(
        version="v1",
        routes=[bad_route, *real.routes[1:]],
        tie_breaker_rules=real.tie_breaker_rules,
    )
    result = check_route_coverage(pack, bad_registry)
    assert any(e.code == "LINT-4" for e in result.errors)


def test_lint4_route_coverage_positive(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_route_coverage(pack, load_route_registry())
    assert result.ok


# ----------------- LINT-5: no orphan cards -----------------


def test_lint5_no_orphan_cards_negative(tmp_path: Path) -> None:
    """An emitted card not referenced by any route → LINT-5 violation."""
    pack_dir = _build_smoke_pack(tmp_path)
    # Plant an extra card not in the registry
    (pack_dir / "99_ORPHAN.md").write_text(
        "# 99 Orphan\n\n## LIVE VERBAL-FIRST OVERWRITE\n",
        encoding="utf-8",
    )
    pack = load_pack(pack_dir)
    result = check_no_orphan_cards(pack, load_route_registry())
    assert any(e.code == "LINT-5" and "99_ORPHAN.md" in e.where for e in result.errors)


def test_lint5_no_orphan_cards_positive(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_no_orphan_cards(pack, load_route_registry())
    assert result.ok


# ----------------- LINT-6: header consistency -----------------


def test_lint6_header_consistency_negative(tmp_path: Path) -> None:
    """A card without the always-on header → LINT-6 violation."""
    pack_dir = _build_smoke_pack(tmp_path)
    bad_card = pack_dir / "05_ARCHITECTURE_CORE.md"
    bad_card.write_text(
        "# 05 Architecture Core\n\nNo header here, sorry.\n",
        encoding="utf-8",
    )
    pack = load_pack(pack_dir)
    result = check_header_consistency(pack, load_route_registry())
    assert any(
        e.code == "LINT-6" and "05_ARCHITECTURE_CORE.md" in e.where
        for e in result.errors
    )


def test_lint6_header_consistency_positive(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_header_consistency(pack, load_route_registry())
    assert result.ok


# ----------------- Integration: aggregate runner -----------------


def test_run_all_validators_accumulates_errors(tmp_path: Path) -> None:
    """Runner combines errors from every validator into one result."""
    pack_dir = _build_smoke_pack(tmp_path)
    # Plant an orphan AND a bad header
    (pack_dir / "99_ORPHAN.md").write_text(
        "# 99 Orphan\n", encoding="utf-8"
    )
    bad = pack_dir / "06_DATA_PLATFORM.md"
    bad.write_text("no header at all", encoding="utf-8")

    result = run_all_validators(pack_dir)
    codes = {e.code for e in result.errors}
    assert "LINT-5" in codes
    assert "LINT-6" in codes
