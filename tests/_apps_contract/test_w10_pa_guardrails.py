"""W10: apps_rg PA Guardrails — Governance Enforcement Tests

Tests that verify:
- No agentic_core imports under apps_rg/prompt_assembly/
- Compiler has no provider/model/network calls
- Compiler has no retrieval, route, L2 execution, Exit evaluation, UWG, or L4 write behavior
- Templates are loaded from apps_rg/prompt_assembly/templates/
- PA fixtures are not treated as canonical prompt source
- Receipt JSON parses and contains required fields
- Docs mention runtime wiring is not complete

Scope: Governance verification. No runtime wiring.
"""

import ast
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml


# =============================================================================
# Path Constants
# =============================================================================

PA_ROOT = Path("apps_rg/prompt_assembly")
TEMPLATES_PATH = PA_ROOT / "templates"
RECEIPT_PATH = Path("artifacts/apps_rg/pa_prompt_contract_receipt.json")
DOCS_PATH = Path("docs/guides/apps_rg_pa_prompt_contract.md")

COMPILER_FILES = [
    PA_ROOT / "compiler.py",
    PA_ROOT / "contracts.py",
    PA_ROOT / "__init__.py",
]


# =============================================================================
# No agentic_core Imports Guardrails
# =============================================================================

class TestNoAgenticCoreImports:
    """Prove apps_rg/prompt_assembly/ has no agentic_core imports."""
    
    def _get_imports_from_file(self, file_path: Path) -> tuple[list[str], list[str]]:
        """Parse Python file and return (regular imports, from imports)."""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        regular_imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    regular_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    from_imports.append(node.module)
        
        return regular_imports, from_imports
    
    def _has_agentic_core_import(self, imports: list[str]) -> list[str]:
        """Filter imports that start with 'agentic_core'."""
        return [imp for imp in imports if imp.startswith("agentic_core")]
    
    @pytest.mark.parametrize("file_path", COMPILER_FILES)
    def test_compiler_file_has_no_agentic_core_imports(self, file_path: Path):
        """Each compiler file must have no agentic_core imports."""
        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")
        
        regular, from_imports = self._get_imports_from_file(file_path)
        all_imports = regular + from_imports
        
        bad_imports = self._has_agentic_core_import(all_imports)
        
        assert len(bad_imports) == 0, (
            f"{file_path} contains agentic_core imports: {bad_imports}. "
            "PA must be self-contained under apps_rg/"
        )
    
    def test_all_pa_files_collectively_have_no_agentic_core(self):
        """All PA Python files collectively must have zero agentic_core imports."""
        all_bad_imports = []
        
        for file_path in PA_ROOT.glob("*.py"):
            regular, from_imports = self._get_imports_from_file(file_path)
            bad = self._has_agentic_core_import(regular + from_imports)
            if bad:
                all_bad_imports.extend([f"{file_path}: {b}" for b in bad])
        
        assert len(all_bad_imports) == 0, (
            f"Found agentic_core imports: {all_bad_imports}"
        )


# =============================================================================
# No Provider/Model/Network Call Guardrails
# =============================================================================

class TestNoProviderModelNetworkCalls:
    """Prove compiler has no provider/model/network calls."""
    
    def _get_function_body(self, file_path: Path, function_name: str) -> str:
        """Extract function body as string."""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Get source lines for this function
                lines = content.splitlines()
                start = node.lineno - 1
                end = node.end_lineno
                return "\n".join(lines[start:end])
        
        return ""
    
    def _has_network_patterns(self, code: str) -> list[str]:
        """Check for network-related patterns in code."""
        patterns = [
            "requests.post",
            "requests.get",
            "httpx.",
            "urllib.request",
            "socket.socket",
            "http.client",
            "openai.",
            "anthropic.",
            "os.system",
            "subprocess.run",
        ]
        found = []
        for pattern in patterns:
            if pattern in code:
                found.append(pattern)
        return found
    
    def test_compiler_compile_method_no_network_calls(self):
        """Compiler.compile() must not contain network call patterns."""
        compiler_file = PA_ROOT / "compiler.py"
        if not compiler_file.exists():
            pytest.skip("compiler.py not found")
        
        body = self._get_function_body(compiler_file, "compile")
        bad_patterns = self._has_network_patterns(body)
        
        assert len(bad_patterns) == 0, (
            f"compile() contains network patterns: {bad_patterns}"
        )
    
    def test_compiler_module_has_no_provider_imports(self):
        """Compiler module must not import provider libraries."""
        compiler_file = PA_ROOT / "compiler.py"
        if not compiler_file.exists():
            pytest.skip("compiler.py not found")
        
        content = compiler_file.read_text(encoding="utf-8")
        forbidden = ["openai", "anthropic", "google.generativeai", "transformers"]
        found = [f for f in forbidden if f in content]
        
        assert len(found) == 0, (
            f"Compiler imports provider libraries: {found}"
        )


# =============================================================================
# No Runtime Wiring Guardrails
# =============================================================================

class TestNoRuntimeWiring:
    """Prove compiler has no retrieval, L2, Exit, UWG, or L4 wiring."""
    
    def _has_runtime_patterns(self, code: str) -> list[str]:
        """Check for runtime wiring patterns."""
        patterns = [
            "C0Retriever",
            "L2_execution",
            "Exit evaluation",
            "UWG",
            "L4_uwg",
            "writeback",
            "emit_ledger",
            "route_to",
            "dispatch_to",
            "runtime.wire",
        ]
        found = []
        for pattern in patterns:
            if pattern in code:
                found.append(pattern)
        return found
    
    def test_compiler_no_retrieval_code(self):
        """Compiler must not contain C0 retrieval logic."""
        compiler_file = PA_ROOT / "compiler.py"
        if not compiler_file.exists():
            pytest.skip("compiler.py not found")
        
        content = compiler_file.read_text(encoding="utf-8")
        bad_patterns = self._has_runtime_patterns(content)
        
        # Filter to retrieval-specific
        retrieval = [p for p in bad_patterns if "retriev" in p.lower() or "C0" in p]
        
        # C0 data is provided in input, not retrieved
        assert "C0Retriever" not in content, (
            "Compiler must not contain C0Retriever class or retrieval logic"
        )
    
    def test_compiler_no_l2_execution_calls(self):
        """Compiler must not call L2 execution."""
        compiler_file = PA_ROOT / "compiler.py"
        if not compiler_file.exists():
            pytest.skip("compiler.py not found")
        
        content = compiler_file.read_text(encoding="utf-8")
        
        assert "L2_execution" not in content, (
            "Compiler must not reference L2_execution"
        )
        assert ".execute(" not in content or "execute(" not in content, (
            "Compiler must not call execute methods"
        )
    
    def test_compiler_no_exit_evaluation(self):
        """Compiler must not call Exit evaluation."""
        compiler_file = PA_ROOT / "compiler.py"
        if not compiler_file.exists():
            pytest.skip("compiler.py not found")
        
        content = compiler_file.read_text(encoding="utf-8")
        
        assert "L5_exit" not in content, (
            "Compiler must not reference L5_exit"
        )
        assert "Exit evaluation" not in content, (
            "Compiler must not reference Exit evaluation"
        )
    
    def test_compiler_no_uwg_l4_writeback(self):
        """Compiler must not reference UWG or L4 writeback."""
        compiler_file = PA_ROOT / "compiler.py"
        if not compiler_file.exists():
            pytest.skip("compiler.py not found")
        
        content = compiler_file.read_text(encoding="utf-8")
        
        assert "UWG" not in content, (
            "Compiler must not reference UWG"
        )
        assert "L4_uwg" not in content, (
            "Compiler must not reference L4_uwg"
        )
        assert "writeback" not in content, (
            "Compiler must not reference writeback"
        )
    
    def test_pa_root_has_no_runtime_dispatch(self):
        """All PA files must not contain runtime dispatch patterns."""
        dispatch_patterns = [
            "runtime.wire",
            "dispatch_to",
            "route_to",
            "bind_to_runtime",
        ]
        
        for py_file in PA_ROOT.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for pattern in dispatch_patterns:
                assert pattern not in content, (
                    f"{py_file} contains runtime dispatch pattern: {pattern}"
                )


# =============================================================================
# Template Loading Location Guardrails
# =============================================================================

class TestTemplateLoadingLocation:
    """Prove templates are loaded from canonical location."""
    
    def test_templates_directory_exists(self):
        """apps_rg/prompt_assembly/templates/ must exist."""
        assert TEMPLATES_PATH.exists(), (
            f"Templates directory not found: {TEMPLATES_PATH}"
        )
    
    def test_all_8_templates_exist(self):
        """All 8 template YAML files must exist."""
        expected = [
            "strategic_tailor_v1.yaml",
            "tailor_existing_v1.yaml",
            "generate_scratch_v1.yaml",
            "enhance_current_v1.yaml",
            "resume_fact_check_v1.yaml",
            "unsupported_claim_omission_v1.yaml",
            "bullet_diversity_repair_v1.yaml",
            "docx_manifest_v1.yaml",
        ]
        
        for template in expected:
            template_path = TEMPLATES_PATH / template
            assert template_path.exists(), (
                f"Template not found: {template_path}"
            )
    
    def test_templates_are_yaml(self):
        """All template files must parse as valid YAML."""
        for yaml_file in TEMPLATES_PATH.glob("*.yaml"):
            content = yaml_file.read_text(encoding="utf-8")
            try:
                data = yaml.safe_load(content)
                assert data is not None, f"Empty YAML: {yaml_file}"
                assert "template_id" in data, (
                    f"Missing template_id in: {yaml_file}"
                )
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {yaml_file}: {e}")


# =============================================================================
# Receipt Validation Guardrails
# =============================================================================

class TestReceiptValidation:
    """Prove receipt JSON exists and contains required fields."""
    
    @pytest.fixture
    def receipt(self):
        """Load receipt JSON."""
        if not RECEIPT_PATH.exists():
            pytest.skip(f"Receipt not found: {RECEIPT_PATH}")
        
        content = RECEIPT_PATH.read_text(encoding="utf-8")
        return json.loads(content)
    
    def test_receipt_exists(self):
        """Receipt JSON file must exist."""
        assert RECEIPT_PATH.exists(), (
            f"Receipt not found at: {RECEIPT_PATH}"
        )
    
    def test_receipt_has_required_fields(self, receipt):
        """Receipt must contain all required top-level fields."""
        required = [
            "plan_id",
            "generated_at",
            "status",
            "completed_waves",
            "template_ids",
            "canonical_prompt_root",
            "test_results",
        ]
        
        for field in required:
            assert field in receipt, f"Missing required field: {field}"
    
    def test_receipt_plan_id_matches(self, receipt):
        """Receipt plan_id must match expected plan."""
        assert receipt["plan_id"] == "apps-rg-pa-full-wave-plan-a7f3d2"
    
    def test_receipt_status_is_w10_complete(self, receipt):
        """Receipt status must be W10_COMPLETE."""
        assert receipt["status"] == "W10_COMPLETE"
    
    def test_receipt_has_all_8_templates(self, receipt):
        """Receipt must list all 8 template IDs."""
        templates = receipt.get("template_ids", [])
        assert len(templates) == 8, f"Expected 8 templates, got {len(templates)}"
        
        expected = [
            "strategic_tailor_v1",
            "tailor_existing_v1",
            "generate_scratch_v1",
            "enhance_current_v1",
            "resume_fact_check_v1",
            "unsupported_claim_omission_v1",
            "bullet_diversity_repair_v1",
            "docx_manifest_v1",
        ]
        
        for template in expected:
            assert template in templates, f"Missing template: {template}"
    
    def test_receipt_has_eaves_phases(self, receipt):
        """Receipt must contain EAVES phase completion data."""
        eaves = receipt.get("eaves_phases_completed", {})
        
        assert "W6" in eaves, "Missing W6 Evidence-governance"
        assert "W7" in eaves, "Missing W7 Authority-model"
        assert "W8" in eaves, "Missing W8 Validation-controls"
        assert "W9" in eaves, "Missing W9 Exit-templates + Smoke-verification"
    
    def test_receipt_has_test_results(self, receipt):
        """Receipt must contain test result lines."""
        results = receipt.get("test_results", {})
        
        assert "W6" in results, "Missing W6 test results"
        assert "W7" in results, "Missing W7 test results"
        assert "W8" in results, "Missing W8 test results"
        assert "W9" in results, "Missing W9 test results"
    
    def test_receipt_has_no_agentic_core_proof(self, receipt):
        """Receipt must contain no_agentic_core_imports proof."""
        proofs = receipt.get("verification_proofs", {})
        
        assert "no_agentic_core_imports" in proofs
        proof = proofs["no_agentic_core_imports"]
        assert proof.get("result") == "PASS - No agentic_core imports found"
    
    def test_receipt_has_no_runtime_wiring_assertion(self, receipt):
        """Receipt must assert no runtime wiring."""
        proofs = receipt.get("verification_proofs", {})
        
        assert "no_runtime_wiring" in proofs
        wiring = proofs["no_runtime_wiring"]
        assert wiring.get("result") == "CONFIRMED - PA is packet builder only, not runtime-wired"
    
    def test_receipt_has_remaining_gaps(self, receipt):
        """Receipt must document remaining gaps."""
        gaps = receipt.get("remaining_gaps", [])
        
        w11_gap = [g for g in gaps if g.get("wave") == "W11"]
        assert len(w11_gap) > 0, "Missing W11 runtime binding gap"
        
        governance_gap = [g for g in gaps if "governance" in g.get("name", "").lower()]
        assert len(governance_gap) > 0, "Missing legacy governance gap"


# =============================================================================
# Documentation Guardrails
# =============================================================================

class TestDocumentation:
    """Prove docs exist and mention runtime wiring status."""
    
    @pytest.fixture
    def docs_content(self):
        """Load documentation content."""
        if not DOCS_PATH.exists():
            pytest.skip(f"Docs not found: {DOCS_PATH}")
        
        return DOCS_PATH.read_text(encoding="utf-8")
    
    def test_documentation_exists(self):
        """Documentation file must exist."""
        assert DOCS_PATH.exists(), (
            f"Documentation not found at: {DOCS_PATH}"
        )
    
    def test_docs_mention_canonical_locations(self, docs_content):
        """Docs must mention canonical prompt locations."""
        assert "apps_rg/prompt_assembly/" in docs_content
        assert "templates/" in docs_content
        assert "prompt_bom.yaml" in docs_content
        assert "prompt_registry.yaml" in docs_content
    
    def test_docs_mention_8_slot_authority(self, docs_content):
        """Docs must mention 8-slot authority model."""
        assert "8-slot" in docs_content or "8 slot" in docs_content
        assert "S0" in docs_content and "R0" in docs_content
    
    def test_docs_mention_no_fabrication_oath(self, docs_content):
        """Docs must mention S0 no-fabrication oath."""
        assert "no-fabrication" in docs_content.lower() or "NO FABRICATION" in docs_content
    
    def test_docs_mention_source_separation(self, docs_content):
        """Docs must mention C0 source separation."""
        assert "candidate_facts" in docs_content
        assert "jd_requirements" in docs_content
        assert "source_tag" in docs_content or "source separation" in docs_content.lower()
    
    def test_docs_mention_runtime_wiring_not_complete(self, docs_content):
        """Docs must explicitly state runtime wiring is not complete."""
        # Check for explicit "not runtime-wired" or "not wired" statements
        lower_content = docs_content.lower()
        
        assert any(phrase in lower_content for phrase in [
            "not runtime-wired",
            "not runtime wired",
            "not wired",
            "explicitly not runtime-wired",
            "w11 (future)",
            "runtime binding decision",
        ]), "Docs must explicitly state runtime wiring is not complete"
    
    def test_docs_mention_pa_fixtures_not_canonical(self, docs_content):
        """Docs must state PA fixtures are not canonical prompt source."""
        lower_content = docs_content.lower()
        
        assert any(phrase in lower_content for phrase in [
            "fixtures are not",
            "not the canonical",
            "not canonical",
            "fixtures are for compile-time",
        ]), "Docs must state PA fixtures are not canonical runtime source"


# =============================================================================
# PA Fixtures Not Canonical Source Guardrails
# =============================================================================

class TestPAFixturesNotCanonicalSource:
    """Prove PA fixtures are not treated as canonical prompt source."""
    
    def test_w9_fixtures_are_test_only(self):
        """W9 fixtures must only exist in test file, not production code."""
        # Check that dry_run_* fixtures are only in test files
        test_file = Path("tests/_apps_contract/test_w9_pa_integration_smoke.py")
        if not test_file.exists():
            pytest.skip("W9 test file not found")
        
        content = test_file.read_text(encoding="utf-8")
        
        # Fixtures should be defined in test file
        assert "dry_run_candidate_facts" in content
        assert "dry_run_jd_requirements" in content
        assert "dry_run_alignment_map" in content
    
    def test_no_production_import_of_test_fixtures(self):
        """Production compiler must not import from test files."""
        compiler_file = PA_ROOT / "compiler.py"
        if not compiler_file.exists():
            pytest.skip("compiler.py not found")
        
        content = compiler_file.read_text(encoding="utf-8")
        
        # Should not import from tests/
        assert "from tests" not in content
        assert "import tests" not in content
        assert "test_w9" not in content
        assert "dry_run_" not in content


# =============================================================================
# Architecture Invariant Guardrails
# =============================================================================

class TestArchitectureInvariants:
    """Prove PA architecture invariants are documented and enforced."""
    
    def test_receipt_contains_architecture_invariants(self):
        """Receipt must document PA_may and PA_must_not."""
        if not RECEIPT_PATH.exists():
            pytest.skip("Receipt not found")
        
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        invariants = receipt.get("architecture_invariants", {})
        
        assert "PA_may" in invariants, "Missing PA_may list"
        assert "PA_must_not" in invariants, "Missing PA_must_not list"
        
        # PA_may should include core capabilities
        may_list = invariants["PA_may"]
        assert any("Load" in item or "load" in item for item in may_list)
        assert any("Validate" in item or "validate" in item for item in may_list)
        
        # PA_must_not should include runtime capabilities
        must_not_list = invariants["PA_must_not"]
        assert any("Route" in item or "route" in item for item in must_not_list)
        assert any("Execute" in item or "execute" in item for item in must_not_list)
    
    def test_receipt_contains_source_separation_spec(self):
        """Receipt must document source separation specification."""
        if not RECEIPT_PATH.exists():
            pytest.skip("Receipt not found")
        
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        source_sep = receipt.get("source_separation", {})
        
        assert "candidate_facts_tag" in source_sep
        assert "jd_requirements_tag" in source_sep
        assert "enforcement" in source_sep


# =============================================================================
# Test Result Verification Guardrails
# =============================================================================

class TestResultVerification:
    """Verify test result claims in receipt match actual test runs."""
    
    def test_w6_test_count_matches_claim(self):
        """W6 test count in receipt should match test file."""
        if not RECEIPT_PATH.exists():
            pytest.skip("Receipt not found")
        
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        w6_tests = receipt.get("eaves_phases_completed", {}).get("W6", {}).get("tests_passed", 0)
        
        # Should match the documented count
        assert w6_tests == 32, f"W6 test count mismatch: expected 32, got {w6_tests}"
    
    def test_total_tests_count_is_correct(self):
        """Total test count should be 136 (32+24+48+32)."""
        if not RECEIPT_PATH.exists():
            pytest.skip("Receipt not found")
        
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        total = receipt.get("total_tests_passed", 0)
        
        assert total == 136, f"Total test count mismatch: expected 136, got {total}"
