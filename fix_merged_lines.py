"""Fix files with merged lines pattern: 'return X    def _run_self_tests'"""
import ast
import re
from pathlib import Path

files_to_check = [
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

# Pattern: something followed by def _run_self_tests on same line
merged_pattern = re.compile(r'(\S)(\s{2,})(def _run_self_tests)')

fixed = 0
failed = 0

for file_path in files_to_check:
    path = Path(file_path)
    if not path.exists():
        print(f"[SKIP] {file_path} - not found")
        continue
    
    content = path.read_text(encoding='utf-8')
    
    # Check if already valid
    try:
        ast.parse(content)
        print(f"[OK] {file_path} - already valid")
        fixed += 1
        continue
    except SyntaxError:
        pass
    
    # Fix merged lines
    if merged_pattern.search(content):
        new_content = merged_pattern.sub(r'\1\n\n\3', content)
        path.write_text(new_content, encoding='utf-8')
        
        try:
            ast.parse(new_content)
            print(f"[FIXED] {file_path}")
            fixed += 1
        except SyntaxError as e:
            print(f"[WARN] {file_path} - line {e.lineno}: {e.msg}")
            failed += 1
    else:
        print(f"[MANUAL] {file_path} - needs manual review")
        failed += 1

print(f"\n{'='*60}")
print(f"Fixed/Valid: {fixed}")
print(f"Need manual: {failed}")
