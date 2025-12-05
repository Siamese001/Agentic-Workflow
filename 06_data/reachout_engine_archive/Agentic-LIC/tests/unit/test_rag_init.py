import importlib


def test_rag_package_exports_expected_symbols():
    module = importlib.import_module("src.lic_agentic.rag")
    for symbol in [
        "ContentStore",
        "EvidenceRegistry",
        "RetrievalPlan",
        "ToolRegistry",
        "ToolResult",
    ]:
        assert hasattr(module, symbol)
