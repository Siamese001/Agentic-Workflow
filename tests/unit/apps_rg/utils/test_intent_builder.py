"""Wave 4.2 — unit tests for apps_rg.utils.intent_builder.

Covers the AppsRgCacheIntent dataclass + cache-key projection and the
build_intent_from_request warm-up stub factory (R1B cache intent payloads).
"""

from __future__ import annotations

from apps_rg.utils.intent_builder import AppsRgCacheIntent, build_intent_from_request


def _intent(**overrides) -> AppsRgCacheIntent:
    base = dict(
        target_company="Acme",
        target_role="SVP",
        target_level="EXECUTIVE",
        policy_hash="ph",
        blueprint_hash="bh",
        tenant_id="t1",
        request_id="r1",
        source_resume_hash="srh",
        generation_mode="strategic_tailor",
        jd_hash="jd",
        brief_hash="brf",
    )
    base.update(overrides)
    return AppsRgCacheIntent(**base)


class TestToCacheKeyDict:
    def test_keys_present(self) -> None:
        d = _intent().to_cache_key_dict()
        assert set(d) == {
            "target_company",
            "target_role",
            "target_level",
            "generation_mode",
            "resume_hash",
            "jd_hash",
            "brief_hash",
            "tenant_id",
            "request_id",
        }

    def test_resume_hash_renamed_from_source_resume_hash(self) -> None:
        d = _intent(source_resume_hash="abc123").to_cache_key_dict()
        assert d["resume_hash"] == "abc123"
        assert "source_resume_hash" not in d

    def test_policy_and_blueprint_hash_excluded(self) -> None:
        d = _intent().to_cache_key_dict()
        assert "policy_hash" not in d
        assert "blueprint_hash" not in d

    def test_values_pass_through(self) -> None:
        d = _intent(target_company="Brown", request_id="req-9").to_cache_key_dict()
        assert d["target_company"] == "Brown"
        assert d["request_id"] == "req-9"


class TestBuildIntentFromRequest:
    def test_returns_intent_with_stub_defaults(self) -> None:
        intent = build_intent_from_request(
            candidate_profile_path="/ignored/path.json",
            target_company="Brown",
            target_role="SVP IT",
            target_level="EXECUTIVE",
            policy_hash="ph",
            blueprint_hash="bh",
            tenant_id="tenant",
            request_id="req",
        )
        assert isinstance(intent, AppsRgCacheIntent)
        assert intent.source_resume_hash == "warm_stub_resume_hash"
        assert intent.generation_mode == "strategic_tailor"
        assert intent.jd_hash == "warm_stub_jd"
        assert intent.brief_hash == "warm_stub_brief"

    def test_passthrough_fields(self) -> None:
        intent = build_intent_from_request(
            candidate_profile_path="x",
            target_company="C",
            target_role="R",
            target_level="L",
            policy_hash="PH",
            blueprint_hash="BH",
            tenant_id="T",
            request_id="RID",
        )
        assert intent.target_company == "C"
        assert intent.policy_hash == "PH"
        assert intent.blueprint_hash == "BH"
        assert intent.tenant_id == "T"
        assert intent.request_id == "RID"

    def test_candidate_profile_path_is_not_persisted(self) -> None:
        intent = build_intent_from_request(
            candidate_profile_path="/secret/profile.json",
            target_company="C",
            target_role="R",
            target_level="L",
            policy_hash="PH",
            blueprint_hash="BH",
            tenant_id="T",
            request_id="RID",
        )
        # path is a warm-up-only stub; it must not leak into any field.
        assert "/secret/profile.json" not in intent.to_cache_key_dict().values()
