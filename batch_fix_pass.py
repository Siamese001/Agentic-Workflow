"""Batch fix empty function bodies by adding pass statements."""
import ast
from pathlib import Path

files_to_fix = [
    ("agentic_core/L0_maintenance/scripts/filesystem_mcp_client.py", 114),
    ("agentic_core/L0_maintenance/scripts/gitkraken_mcp_client.py", 193),
    ("agentic_core/L1_cognition/thought_engine/CanonHealerAgent.py", 536),
    ("agentic_core/L1_cognition/thought_engine/strategic_planner.py", 312),
    ("agentic_core/L2_execution/ToolRegistry/figma_client_sovereign.py", 112),
    ("agentic_core/L3_orchestration/workflow_engines/agent_factory.py", 186),
    ("agentic_core/L3_orchestration/workflow_engines/agent_gym_impl.py", 258),
    ("agentic_core/L3_orchestration/workflow_engines/context_curator_impl.py", 236),
    ("agentic_core/L3_orchestration/workflow_engines/mcp_router_sovereign.py", 158),
    ("agentic_core/L4_state/ValidationContext/knowledge_graph_sovereign_graph_client.py", 249),
    ("agentic_core/L4_state/ValidationContext/storage.py", 399),
    ("agentic_core/L5_safety/guardrails/BiasDetectorAgent.py", 57),
    ("agentic_core/L5_safety/guardrails/ConstitutionalReviewerAgent.py", 115),
    ("agentic_core/L5_safety/guardrails/PIISanitizerAgent.py", 65),
    ("agentic_core/L5_safety/guardrails/PromptInjectionDetectorAgent.py", 101),
    ("agentic_core/L5_safety/guardrails/llm_router_mcp_client.py", 74),
    ("agentic_core/L5_safety/guardrails/multi_provider_router_agent.py", 668),
    ("agentic_core/observability/metrics/BenchmarkingAgent.py", 410),
    ("agentic_core/utils/core_extensions/git.py", 154),
    ("agentic_core/utils/core_extensions/http.py", 182),
    ("agentic_core/utils/core_extensions/pinecone.py", 137),
    ("agentic_core/utils/core_extensions/redis.py", 186),
    ("agentic_core/utils/core_extensions/sovereignty_auditor.py", 188),
    ("apps_lic/engines/outreach_engine/rag/campaign_rag.py", 70),
    ("apps_rg/engines/resume_generator.py", 226),
]

# Try block files
try_block_files = [
    ("agentic_core/L1_cognition/thought_engine/sovereign_cognitive_plane.py", 35),
    ("agentic_core/L1_cognition/thought_engine/sovereign_cognitive_plane_with_streamer.py", 32),
]

def add_pass_after_line(file_path: str, line_num: int) -> bool:
    """Add pass statement after the specified line."""
    try:
        path = Path(file_path)
        lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
        
        if line_num > len(lines):
            print(f"  [SKIP] Line {line_num} exceeds file length")
            return False
        
        # Get the line and determine indentation
        target_line = lines[line_num - 1]
        base_indent = len(target_line) - len(target_line.lstrip())
        body_indent = base_indent + 4
        
        # Check if next line already has proper indentation
        if line_num < len(lines):
            next_line = lines[line_num]
            next_indent = len(next_line) - len(next_line.lstrip())
            if next_indent >= body_indent and next_line.strip():
                print(f"  [SKIP] Already has body content")
                return False
        
        # Insert pass statement
        pass_line = ' ' * body_indent + 'pass\n'
        lines.insert(line_num, pass_line)
        
        path.write_text(''.join(lines), encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

fixed = 0
failed = 0

print("Fixing function definition files...")
for file_path, line_num in files_to_fix:
    print(f"Processing {file_path}:{line_num}")
    if add_pass_after_line(file_path, line_num):
        # Verify fix
        try:
            ast.parse(Path(file_path).read_text(encoding='utf-8'))
            print(f"  [OK] Fixed and verified")
            fixed += 1
        except SyntaxError as e:
            print(f"  [WARN] Fixed but still has errors: {e.msg} at line {e.lineno}")
            failed += 1
    else:
        failed += 1

print("\nFixing try block files...")
for file_path, line_num in try_block_files:
    print(f"Processing {file_path}:{line_num}")
    if add_pass_after_line(file_path, line_num):
        try:
            ast.parse(Path(file_path).read_text(encoding='utf-8'))
            print(f"  [OK] Fixed and verified")
            fixed += 1
        except SyntaxError as e:
            print(f"  [WARN] Fixed but still has errors: {e.msg} at line {e.lineno}")
            failed += 1
    else:
        failed += 1

print(f"\n{'='*60}")
print(f"Fixed: {fixed}")
print(f"Failed/Skipped: {failed}")
