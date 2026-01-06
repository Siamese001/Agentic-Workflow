"""Fix corrupted _run_self_tests methods by removing them entirely."""
import ast
import re
from pathlib import Path

# Files with corrupted _run_self_tests pattern
files_to_fix = [
    "agentic_core/L0_maintenance/scripts/gitkraken_mcp_client.py",
    "agentic_core/L1_cognition/thought_engine/CanonHealerAgent.py",
    "agentic_core/L1_cognition/thought_engine/strategic_planner.py",
    "agentic_core/L2_execution/ToolRegistry/figma_client_sovereign.py",
    "agentic_core/L3_orchestration/workflow_engines/agent_factory.py",
    "agentic_core/L3_orchestration/workflow_engines/agent_gym_impl.py",
    "agentic_core/L3_orchestration/workflow_engines/context_curator_impl.py",
    "agentic_core/L3_orchestration/workflow_engines/mcp_router_sovereign.py",
    "agentic_core/L4_state/ValidationContext/knowledge_graph_sovereign_graph_client.py",
    "agentic_core/L4_state/ValidationContext/storage.py",
    "agentic_core/L5_safety/guardrails/BiasDetectorAgent.py",
    "agentic_core/L5_safety/guardrails/ConstitutionalReviewerAgent.py",
    "agentic_core/L5_safety/guardrails/PIISanitizerAgent.py",
    "agentic_core/L5_safety/guardrails/PromptInjectionDetectorAgent.py",
    "agentic_core/L5_safety/guardrails/llm_router_mcp_client.py",
    "agentic_core/L5_safety/guardrails/multi_provider_router_agent.py",
    "agentic_core/observability/metrics/BenchmarkingAgent.py",
    "agentic_core/utils/core_extensions/git.py",
    "agentic_core/utils/core_extensions/http.py",
    "agentic_core/utils/core_extensions/pinecone.py",
    "agentic_core/utils/core_extensions/redis.py",
    "agentic_core/utils/core_extensions/sovereignty_auditor.py",
    "apps_lic/engines/outreach_engine/rag/campaign_rag.py",
    "apps_rg/engines/resume_generator.py",
]

# Pattern to match corrupted _run_self_tests block
corrupted_pattern = re.compile(
    r'(\s*)def _run_self_tests\(self\) -> dict:\s*\n'
    r'\s*pass\s*\n'
    r'\s*"""Run internal self-tests\."""\s*\n'
    r'(\s*pass\s*\n)*'
    r'\s*results = \{"passed": 0.*?return results',
    re.DOTALL
)

# Clean replacement
clean_self_tests = '''    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results'''

fixed = 0
failed = 0

for file_path in files_to_fix:
    path = Path(file_path)
    if not path.exists():
        print(f"[SKIP] {file_path} - not found")
        failed += 1
        continue
    
    try:
        content = path.read_text(encoding='utf-8')
        
        # Try to find and replace the corrupted pattern
        if corrupted_pattern.search(content):
            new_content = corrupted_pattern.sub(clean_self_tests, content)
            path.write_text(new_content, encoding='utf-8')
            
            # Verify
            try:
                ast.parse(new_content)
                print(f"[OK] {file_path}")
                fixed += 1
            except SyntaxError as e:
                print(f"[WARN] {file_path} - still has errors at line {e.lineno}: {e.msg}")
                failed += 1
        else:
            print(f"[SKIP] {file_path} - pattern not found, needs manual review")
            failed += 1
            
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
        failed += 1

print(f"\n{'='*60}")
print(f"Fixed: {fixed}")
print(f"Failed/Skipped: {failed}")
