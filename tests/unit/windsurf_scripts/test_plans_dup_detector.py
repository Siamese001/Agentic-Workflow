"""
Unit tests for .claude/governance/scripts/_legacy_windsurf/_plans_dup_detector.py.

Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2c/d).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / ".claude" / "governance" / "scripts" / "_plans_dup_detector.py"


def _load():
    spec = importlib.util.spec_from_file_location("_plans_dup_detector", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_plans_dup_detector"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


# -------------------------------------------------------------------
# extract_plans_post_invocations
# -------------------------------------------------------------------


PLANS_DB_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
PLANS_DS_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"


def _make_invoke(db_id: str, slug: str, *, name: str = "API-post-page") -> str:
    return (
        f'<invoke name="{name}">'
        f'<parameter name="parent">'
        f'{{"type": "database_id", "database_id": "{db_id}"}}'
        f'</parameter>'
        f'<parameter name="properties">'
        f'{{"Slug": {{"title": [{{"text": {{"content": "{slug}"}}}}]}}, '
        f'"Status": {{"select": {{"name": "Not Started"}}}}}}'
        f'</parameter>'
        f'</invoke>'
    )


def test_extract_plans_post_via_database_id(mod):
    text = _make_invoke(PLANS_DB_ID, "test-plan-aaaaaa")
    invs = mod.extract_plans_post_invocations(text)
    assert len(invs) == 1
    assert invs[0].slug == "test-plan-aaaaaa"


def test_extract_plans_post_via_data_source_id(mod):
    text = _make_invoke(PLANS_DS_ID, "test-plan-bbbbbb")
    invs = mod.extract_plans_post_invocations(text)
    assert len(invs) == 1
    assert invs[0].slug == "test-plan-bbbbbb"


def test_extract_handles_mcp_prefix(mod):
    text = _make_invoke(PLANS_DB_ID, "test-plan-cccccc", name="API-post-page")
    text = text.replace('name="API-post-page"', 'name="mcp7_API-post-page"')
    invs = mod.extract_plans_post_invocations(text)
    assert len(invs) == 1


def test_extract_skips_non_plans_db(mod):
    text = _make_invoke("aa8d2507-101e-4384-81d9-60ea3fe33876", "test-plan-aaaaaa")
    assert mod.extract_plans_post_invocations(text) == []


def test_extract_skips_patch_calls(mod):
    """Only POST counts — PATCH is not a duplicate-creator."""
    text = _make_invoke(PLANS_DB_ID, "test-plan-aaaaaa", name="API-patch-page")
    assert mod.extract_plans_post_invocations(text) == []


def test_extract_empty_slug_when_unparseable(mod):
    """POST without a slug is captured but slug is empty."""
    text = (
        '<invoke name="API-post-page">'
        f'<parameter name="parent">{{"database_id": "{PLANS_DB_ID}"}}</parameter>'
        '<parameter name="properties">{"Status": {"select": {"name": "X"}}}</parameter>'
        '</invoke>'
    )
    invs = mod.extract_plans_post_invocations(text)
    assert len(invs) == 1
    assert invs[0].slug == ""


def test_extract_multiple_invocations_in_one_response(mod):
    text = (
        _make_invoke(PLANS_DB_ID, "first-plan-aaaaaa")
        + "\n\nSome prose between\n\n"
        + _make_invoke(PLANS_DB_ID, "second-plan-bbbbbb")
    )
    invs = mod.extract_plans_post_invocations(text)
    assert [i.slug for i in invs] == ["first-plan-aaaaaa", "second-plan-bbbbbb"]


def test_extract_empty_text(mod):
    assert mod.extract_plans_post_invocations("") == []


# -------------------------------------------------------------------
# find_duplicate_groups
# -------------------------------------------------------------------


def test_find_duplicates_dict_input(mod):
    snapshot = {
        "lonely-plan-aaaaaa": [{"id": "p1", "status": "Completed"}],
        "twins-plan-bbbbbb": [
            {"id": "p2", "status": "In Progress"},
            {"id": "p3", "status": "Not Started"},
        ],
    }
    groups = mod.find_duplicate_groups(snapshot)
    assert len(groups) == 1
    assert groups[0].slug == "twins-plan-bbbbbb"
    assert set(groups[0].page_ids) == {"p2", "p3"}


def test_find_duplicates_list_input(mod):
    snapshot = [
        {"slug": "lonely-aaaaaa", "id": "p1", "status": "Completed"},
        {"slug": "twins-bbbbbb", "id": "p2", "status": "In Progress"},
        {"slug": "twins-bbbbbb", "id": "p3", "status": "Not Started"},
    ]
    groups = mod.find_duplicate_groups(snapshot)
    assert len(groups) == 1
    assert groups[0].slug == "twins-bbbbbb"


def test_find_duplicates_excludes_archived_rows(mod):
    snapshot = [
        {"slug": "twins-bbbbbb", "id": "p2", "status": "Completed", "in_trash": False},
        {"slug": "twins-bbbbbb", "id": "p3", "status": "Not Started", "in_trash": True},
    ]
    # Only one ACTIVE row -> not a duplicate.
    assert mod.find_duplicate_groups(snapshot) == []


def test_find_duplicates_excludes_archived_flag(mod):
    snapshot = [
        {"slug": "twins-bbbbbb", "id": "p2", "status": "Completed", "archived": False},
        {"slug": "twins-bbbbbb", "id": "p3", "status": "Not Started", "archived": True},
    ]
    assert mod.find_duplicate_groups(snapshot) == []


def test_find_duplicates_no_dupes(mod):
    snapshot = {
        "alpha-aaaaaa": [{"id": "p1", "status": "Completed"}],
        "beta-bbbbbb": [{"id": "p2", "status": "In Progress"}],
    }
    assert mod.find_duplicate_groups(snapshot) == []


def test_find_duplicates_ordered_by_slug(mod):
    snapshot = {
        "zeta-zzzzzz": [{"id": "p1"}, {"id": "p2"}],
        "alpha-aaaaaa": [{"id": "p3"}, {"id": "p4"}],
    }
    groups = mod.find_duplicate_groups(snapshot)
    slugs = [g.slug for g in groups]
    assert slugs == sorted(slugs)
