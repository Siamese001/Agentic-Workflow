"""apps_research UWG writer regression tests."""

from __future__ import annotations


def test_commit_brief_record_supplies_l5_certification_ref() -> None:
    from apps_research.integrations.governed_research_run import GovernedE2ERunRecord
    from apps_research.integrations.research_brief_uwg_writer import commit_brief_record

    captured = {}

    class _Receipt:
        commit_receipt_id = "receipt-research-brief-test"

    class _Gateway:
        last_snapshot_id = "snapshot-before"

        def commit(self, *, commit_request, state_diffs, rollback_plan, refresh_plan):
            captured["commit_request"] = commit_request
            captured["state_diffs"] = state_diffs
            captured["rollback_plan"] = rollback_plan
            captured["refresh_plan"] = refresh_plan
            return _Receipt(), None, None

    run_record = GovernedE2ERunRecord(
        run_id="research-run-test",
        topic="Anthropic",
        l1_sub_queries=("Anthropic",),
        l1_fallback=False,
        l0_intent="research",
        l0_target="research_assembly",
        l0_confidence=0.9,
        l0_fallback=False,
        c0_raw_count=3,
        c0_shaped_count=3,
        c0_collection="process_docs",
        disposition="proceed",
        gate_disposition="allow_response",
        grounded=True,
        citation_count=3,
        support_coverage=0.9,
        l6_ingested=True,
        error="",
        research_depth_profile="COMPANY_BRIEF_STANDARD",
        fec_run_context={"company_brief": {"company_brief_text": "brief"}},
    )

    brief = commit_brief_record(run_record, gateway=_Gateway())

    assert brief.commit_receipt_ref == "receipt-research-brief-test"
    assert captured["commit_request"].l5_certification_ref
