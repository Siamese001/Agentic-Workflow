#!/usr/bin/env python3
import ast
from pathlib import Path

agents_to_check = [
    "ArchitectureGovernorAgent",
    "CognitiveDispositionAgent",
    "FileClassificationAgent",
    "FilesystemSSOTReconcilerAgent",
    "GravityLeakHealerAgent",
    "HierarchyAgent",
    "LocationHealerAgent",
    "RootHygieneAgent",
]

base = Path("c:/Git/Agentic-Workflow/agentic_core/L5_safety/reasoning")
results = []

for agent in agents_to_check:
    file_path = base / f"{agent}.py"
    if not file_path.exists():
        results.append(
            {
                "agent": agent,
                "exists": False,
                "has_llm": False,
                "has_prompt": False,
                "has_ast": False,
                "has_regex": False,
                "has_path": False,
                "methods": 0,
            }
        )
        continue

    with open(file_path, encoding="utf-8") as f:
        content = f.read()
        try:
            tree = ast.parse(content)
        except:  # guardian: allow-silent-swallow
            tree = None

    # Check for LLM/reasoning indicators
    has_llm = any(
        x in content.lower()
        for x in [
            "openai",
            "anthropic",
            "generate_text",
            "llm_call",
            "model.generate",
            "completion",
            "chat.completions",
        ]
    )
    has_prompt = (
        "prompt" in content.lower() and "meta_prompt" in content.lower()
    ) or "prompt_template" in content.lower()

    # Check for deterministic indicators
    has_ast_parse = "ast.parse" in content or "ast.walk" in content
    has_regex = "re.match" in content or "re.search" in content or "re.compile" in content
    has_path_ops = "Path(" in content and (".exists()" in content or ".rglob" in content)

    # Count methods
    method_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)) if tree else 0

    results.append(
        {
            "agent": agent,
            "exists": True,
            "has_llm": has_llm,
            "has_prompt": has_prompt,
            "has_ast": has_ast_parse,
            "has_regex": has_regex,
            "has_path": has_path_ops,
            "methods": method_count,
        }
    )

print("Agent|Exists|LLM|Prompt|AST|Regex|Path|Methods|Recommendation")
print("-" * 100)
for r in results:
    if not r["exists"]:
        print(f"{r['agent']}|False|N/A|N/A|N/A|N/A|N/A|N/A|File not found")
        continue

    # Determine if truly needs to be an agent
    needs_agent = r["has_llm"] or r["has_prompt"]
    recommendation = (
        "KEEP as Agent (uses LLM)" if needs_agent else "CONVERT to Script/Validator (deterministic)"
    )

    print(
        f"{r['agent']}|True|{r['has_llm']}|{r['has_prompt']}|{r['has_ast']}|{r['has_regex']}|{r['has_path']}|{r['methods']}|{recommendation}"
    )
