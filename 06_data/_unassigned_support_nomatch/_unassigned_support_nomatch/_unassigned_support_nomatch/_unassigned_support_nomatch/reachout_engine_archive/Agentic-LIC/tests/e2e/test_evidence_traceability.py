from src.lic_agentic.rag.evidence_registry import EvidenceRegistry


def test_mapping():
    registry = EvidenceRegistry()
    artifact_id = registry.upsert(
        scope="company",
        company_id="ACME",
        source_url="http://example.com",
        summary="ACME hit revenue goals",
        anchor_date="2025-10-01",
        confidence=0.9,
        used_in_section="value_wedge",
    )
    assert artifact_id in registry
    stored = registry.get(artifact_id)
    assert stored and stored.used_in_section == "value_wedge"
