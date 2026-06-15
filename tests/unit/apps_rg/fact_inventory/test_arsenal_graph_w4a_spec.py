from __future__ import annotations

from apps_rg.fact_inventory import arsenal_graph_w4a_spec as spec


def test_agentic_capability_domains_have_unique_ids_and_valid_pillars() -> None:
    domain_ids = [row["domain_id"] for row in spec.AGENTIC_CAPABILITY_DOMAINS]

    assert len(domain_ids) == 14
    assert len(domain_ids) == len(set(domain_ids))
    assert all(row["label"] for row in spec.AGENTIC_CAPABILITY_DOMAINS)
    assert all(row["pillar"].startswith("pillar_") for row in spec.AGENTIC_CAPABILITY_DOMAINS)


def test_identity_node_refs_declared_epochs_and_agentic_epoch_refs_all_domains() -> None:
    epoch_ids = {row["node_id"] for row in spec.CAREER_EPOCHS}
    agentic_domains = {row["domain_id"] for row in spec.AGENTIC_CAPABILITY_DOMAINS}

    assert set(spec.IDENTITY_NODE["epoch_ids"]) == epoch_ids
    agentic_epoch = next(
        row
        for row in spec.CAREER_EPOCHS
        if row["node_id"] == "epoch_agentic_ai_runtime_architecture"
    )
    assert set(agentic_epoch["capability_domain_ids"]) == agentic_domains


def test_agentic_skill_template_rows_are_well_formed() -> None:
    rows = spec._AGENTIC_ROW_TEMPLATE

    assert rows
    assert len({row[0] for row in rows}) == len(rows)
    for skill_id, label, source_concepts, snippet, _fact_links, repo_files in rows:
        assert skill_id.startswith("skill_")
        assert label
        assert source_concepts
        assert snippet.endswith(".")
        assert isinstance(repo_files, list)
