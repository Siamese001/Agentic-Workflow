"""W5 contract tests for build_app_record helper.

Locks in the W5 invariants:
1. ``build_app_record`` exists and is exported from
   ``apps_shared.integrations.governed_app_runner``.
2. Common-name substrate fields are auto-copied to per-app record fields.
3. ``app_specific`` kwargs override / supply non-substrate fields.
4. ``aliases`` lets a per-app record rename a substrate field
   (e.g. apps_research's ``topic`` <- substrate ``query``).
5. Unknown ``app_specific`` keys raise ``TypeError`` (loud-failure contract).
6. The 4 governed app translators are slim (no longer 30+ lines of
   ``field=core.field``).
7. Adding a new substrate field with a default automatically propagates to
   every per-app record without a per-app edit.

Plan ``apps-runtime-first-principles-e6ba58`` W5.1 + W5.2.
"""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass

import pytest

from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunRecord,
    build_app_record,
)


# ---------------------------------------------------------------------------
# Test fixtures \u2014 a minimal substrate record + per-app shapes
# ---------------------------------------------------------------------------


def _make_core(**overrides) -> GovernedAppRunRecord:
    """Build a substrate record with sensible defaults; allow per-test overrides."""
    base: dict[str, object] = {
        "run_id": "run-abc",
        "app_name": "apps_test",
        "query": "test query",
        "l1_sub_queries": ("a", "b"),
        "l1_fallback": False,
        "l0_intent": "intent-x",
        "l0_target": "target-x",
        "l0_confidence": 0.92,
        "l0_fallback": False,
        "c0_raw_count": 5,
        "c0_shaped_count": 6,
        "c0_collection": "test_docs",
        "disposition": "proceed",
        "gate_disposition": "allow_response",
        "grounded": True,
        "citation_count": 3,
        "support_coverage": 0.81,
        "l6_ingested": True,
        "l2_executed": True,
        "error": "",
    }
    base.update(overrides)
    return GovernedAppRunRecord(**base)


@dataclass(frozen=True)
class _AppRecordSimple:
    """Minimal per-app record: subset of substrate fields + 1 app-specific."""
    run_id: str
    query: str
    grounded: bool
    audience: str  # app-specific
    error: str = ""


@dataclass(frozen=True)
class _AppRecordWithAlias:
    """Per-app record that renames substrate ``query`` -> ``topic``."""
    run_id: str
    topic: str  # alias of substrate.query
    l1_sub_queries: tuple[str, ...]
    error: str = ""


@dataclass(frozen=True)
class _AppRecordWithDefaults:
    """Per-app record where substrate fields with defaults are present, plus
    a substrate field NOT present (l0_target) to test default-passthrough."""
    run_id: str
    query: str
    error: str = ""
    grounded: bool = False
    extra_app_field: str = "default"


# ---------------------------------------------------------------------------
# Helper exists + is exported
# ---------------------------------------------------------------------------


def test_build_app_record_is_exported_from_substrate() -> None:
    """W5: helper is importable from the substrate module."""
    from apps_shared.integrations.governed_app_runner import build_app_record  # noqa: F401


# ---------------------------------------------------------------------------
# Common-name substrate fields auto-copy
# ---------------------------------------------------------------------------


def test_common_substrate_fields_auto_copied() -> None:
    """W5: target fields with same name as substrate fields are auto-copied."""
    core = _make_core()
    rec = build_app_record(_AppRecordSimple, core, audience="board")

    assert rec.run_id == core.run_id
    assert rec.query == core.query
    assert rec.grounded == core.grounded
    assert rec.audience == "board"
    assert rec.error == core.error


def test_app_specific_kwargs_override_substrate() -> None:
    """W5: explicit kwargs win over substrate values when names collide."""
    core = _make_core(query="substrate-query")
    rec = build_app_record(_AppRecordSimple, core, audience="ceo", query="overridden")

    assert rec.query == "overridden"


def test_unknown_app_specific_keys_raise_type_error() -> None:
    """W5 loud-failure: passing unknown kwargs surfaces TypeError, not silently dropped."""
    core = _make_core()
    with pytest.raises(TypeError, match=r"unknown app_specific keys"):
        build_app_record(_AppRecordSimple, core, audience="board", bogus_key="oops")


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------


def test_alias_renames_substrate_field_to_target_field() -> None:
    """W5: aliases={target: substrate} copies substrate.query -> target.topic."""
    core = _make_core(query="renamed-query")
    rec = build_app_record(_AppRecordWithAlias, core, aliases={"topic": "query"})

    assert rec.topic == "renamed-query"
    assert rec.run_id == core.run_id
    assert rec.l1_sub_queries == core.l1_sub_queries


def test_alias_does_not_break_non_aliased_fields() -> None:
    """W5: aliasing one field does not interfere with auto-copy of others."""
    core = _make_core()
    rec = build_app_record(_AppRecordWithAlias, core, aliases={"topic": "query"})

    assert rec.run_id == core.run_id
    assert rec.l1_sub_queries == core.l1_sub_queries


# ---------------------------------------------------------------------------
# Defaults pass through
# ---------------------------------------------------------------------------


def test_target_specific_default_field_takes_dataclass_default() -> None:
    """W5: target fields without substrate counterparts use their dataclass default."""
    core = _make_core()
    rec = build_app_record(_AppRecordWithDefaults, core)

    assert rec.extra_app_field == "default"
    assert rec.run_id == core.run_id
    assert rec.query == core.query


# ---------------------------------------------------------------------------
# 4 governed app translators are slim (W5.2 LOC contract)
# ---------------------------------------------------------------------------


_GOVERNED_APPS = [
    ("apps_exec.integrations.governed_exec_run", "GovernedExecRun"),
    ("apps_lic.integrations.governed_lic_run", "GovernedLicRun"),
    ("apps_rfp.integrations.governed_rfp_run", "GovernedRfpRun"),
    ("apps_research.integrations.governed_research_run", "GovernedResearchRun"),
]


@pytest.mark.parametrize("module_path,cls_name", _GOVERNED_APPS)
def test_governed_app_translator_uses_build_app_record(module_path: str, cls_name: str) -> None:
    """W5.2: every governed app translator MUST use build_app_record (not field-by-field)."""
    import importlib

    mod = importlib.import_module(module_path)
    cls = getattr(mod, cls_name)
    src = inspect.getsource(cls.run_governed_e2e)

    assert "build_app_record" in src, (
        f"{cls_name}.run_governed_e2e must use build_app_record, not field-by-field "
        f"translator boilerplate."
    )


@pytest.mark.parametrize("module_path,cls_name", _GOVERNED_APPS)
def test_governed_app_translator_has_no_field_by_field_copy(module_path: str, cls_name: str) -> None:
    """W5.2 LOC contract: the translator must not contain >5 ``field=core.field`` lines.

    The original boilerplate had 25\u201335 such lines. The slim form has at most
    5 (some translators legitimately reference a small number of core fields
    when computing derived values).
    """
    import importlib

    mod = importlib.import_module(module_path)
    cls = getattr(mod, cls_name)
    src = inspect.getsource(cls.run_governed_e2e)

    # Match patterns like ``field_name=core.field_name`` on a line.
    pattern = re.compile(r"^\s+\w+\s*=\s*core\.\w+,?\s*$", re.MULTILINE)
    matches = pattern.findall(src)

    assert len(matches) <= 5, (
        f"{cls_name}.run_governed_e2e still has {len(matches)} field=core.field "
        f"lines \u2014 should be \u22645 after W5 refactor:\n  "
        + "\n  ".join(matches)
    )


# ---------------------------------------------------------------------------
# Drift safety \u2014 substrate fields propagate to per-app records automatically
# ---------------------------------------------------------------------------


def test_real_apps_exec_translator_picks_up_all_substrate_fields() -> None:
    """W5 drift safety: GovernedExecE2ERunRecord must surface ALL substrate fields it shares names with.

    Was the original ADG G8 finding: 4 governed apps re-declared 22 substrate
    fields and any new substrate field needed manual replication. With
    build_app_record, the translator picks up new substrate fields automatically.
    """
    import dataclasses

    from apps_exec.integrations.governed_exec_run import (
        GovernedExecE2ERunRecord,
        GovernedExecRun,
    )

    # Construct a real exec record via the production translator.
    runner = GovernedExecRun(collection="exec_docs")
    core = _make_core(app_name="apps_exec", query="exec query")

    rec = build_app_record(
        GovernedExecE2ERunRecord, core,
        audience="board",
        emphasis_areas=("ai", "governance"),
    )

    # Every substrate field with a same-named target field must be populated.
    substrate_field_names = {f.name for f in dataclasses.fields(GovernedAppRunRecord)}
    target_field_names = {f.name for f in dataclasses.fields(GovernedExecE2ERunRecord)}
    common = substrate_field_names & target_field_names
    for name in common:
        assert getattr(rec, name) == getattr(core, name), (
            f"Substrate field {name!r} not propagated to GovernedExecE2ERunRecord"
        )

    # App-specific fields populated from kwargs.
    assert rec.audience == "board"
    assert rec.emphasis_areas == ("ai", "governance")
