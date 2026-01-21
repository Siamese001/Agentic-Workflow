"""EvidenceRegistry behavior tests."""

from src.lic_agentic.rag.evidence_registry import EvidenceRegistry


def test_evidence_registry_list_filters_scope():
    registry = EvidenceRegistry()
    a1 = registry.upsert(
        "company",
        "ACME",
        "http://example.com/a",
        "Summary A",
        "2025-01-01",
        0.9,
        "value_wedge",
    )
    _ = registry.upsert(
        "contact",
        "ACME",
        "http://example.com/b",
        "Summary B",
        "2025-01-02",
        0.8,
        "personalization",
    )
    assert registry.get(a1).summary == "Summary A"
    assert len(registry.list()) == 2
    company_records = registry.list(scope="company")
    assert len(company_records) == 1
    assert company_records[0].artifact_id == a1
    manual_id = "artifact-123"
    registry.upsert(
        "company",
        "ACME",
        "http://example.com/c",
        "Summary C",
        "2025-01-03",
        0.7,
        "value_wedge",
        artifact_id=manual_id,
    )
    assert manual_id in registry
    assert registry.get("missing") is None
    assert registry.list(scope="unknown") == []
