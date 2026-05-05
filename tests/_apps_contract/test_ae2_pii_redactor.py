"""tests._apps_contract.test_ae2_pii_redactor — AE-2 PII redactor tests.

Plan: apps-eval-harness-phase2-b5f3c1 W2/AE-2.
"""

from __future__ import annotations

import pytest
from apps_eval.integrations.pii_redactor import PiiRedactor, PiiRedactorConfig


class TestPiiRedactorDefaults:
    def test_mask_field_replaced(self) -> None:
        r = PiiRedactor()
        out = r.redact({"name": "Alice Smith", "score": 0.9})
        assert out["name"] == "[REDACTED]"
        assert out["score"] == 0.9

    def test_hash_field_replaced_with_prefix(self) -> None:
        r = PiiRedactor()
        out = r.redact({"email": "alice@example.com"})
        assert out["email"].startswith("sha256:")
        assert out["email"] != "alice@example.com"

    def test_hash_stable_across_calls(self) -> None:
        r = PiiRedactor()
        o1 = r.redact({"email": "alice@example.com"})
        o2 = r.redact({"email": "alice@example.com"})
        assert o1["email"] == o2["email"]

    def test_non_pii_field_preserved(self) -> None:
        r = PiiRedactor()
        out = r.redact({"app_id": "apps_rg", "score": 0.85})
        assert out["app_id"] == "apps_rg"
        assert out["score"] == 0.85

    def test_empty_row_returns_empty(self) -> None:
        r = PiiRedactor()
        assert r.redact({}) == {}

    def test_non_mapping_input_returns_empty(self) -> None:
        r = PiiRedactor()
        assert r.redact("not-a-dict") == {}  # type: ignore[arg-type]

    def test_does_not_mutate_input(self) -> None:
        r = PiiRedactor()
        original = {"name": "Bob", "score": 1.0}
        r.redact(original)
        assert original["name"] == "Bob"


class TestPiiRedactorCustomConfig:
    def test_drop_policy_removes_key(self) -> None:
        cfg = PiiRedactorConfig(field_policies={"secret": "drop"})
        r = PiiRedactor(cfg)
        out = r.redact({"secret": "abc", "keep": "yes"})
        assert "secret" not in out
        assert out["keep"] == "yes"

    def test_custom_mask_field(self) -> None:
        cfg = PiiRedactorConfig(field_policies={"custom_field": "mask"})
        r = PiiRedactor(cfg)
        out = r.redact({"custom_field": "sensitive", "other": 42})
        assert out["custom_field"] == "[REDACTED]"
        assert out["other"] == 42

    def test_recursive_scrubs_nested_dict(self) -> None:
        cfg = PiiRedactorConfig(field_policies={"email": "hash"}, recursive=True)
        r = PiiRedactor(cfg)
        out = r.redact({"meta": {"email": "x@y.com", "count": 1}})
        assert out["meta"]["email"].startswith("sha256:")
        assert out["meta"]["count"] == 1

    def test_recursive_scrubs_list_of_dicts(self) -> None:
        cfg = PiiRedactorConfig(field_policies={"name": "mask"}, recursive=True)
        r = PiiRedactor(cfg)
        out = r.redact({"items": [{"name": "Alice"}, {"name": "Bob"}]})
        for item in out["items"]:
            assert item["name"] == "[REDACTED]"

    def test_non_recursive_skips_nested(self) -> None:
        cfg = PiiRedactorConfig(field_policies={"email": "hash"}, recursive=False)
        r = PiiRedactor(cfg)
        out = r.redact({"meta": {"email": "x@y.com"}})
        assert out["meta"]["email"] == "x@y.com"


class TestPiiRedactorIntegration:
    def test_is_stub_false(self) -> None:
        assert PiiRedactor.IS_STUB is False

    def test_wires_into_production_log_miner(self) -> None:
        from ops_scripts.calibration.production_log_miner import (
            set_redactor,
            is_stub_redactor,
        )
        r = PiiRedactor()
        set_redactor(r.redact)
        assert not is_stub_redactor()
