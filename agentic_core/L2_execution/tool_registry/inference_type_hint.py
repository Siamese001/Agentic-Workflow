# InferenceTypeHintAgent - Atomic Validator (Gated LLM Healing)
# Territory: agentic_core/L2_execution/tool_registry
# Canon Alignment: Enforces precise, inference-based type hints using SubAtomicEngine
# Surgery Scope: Single file — LLM-powered annotation
# Gated: Only active when RUN_HIERARCHY_HEALING=True (due to LLM cost/rate limits)

import ast
from pathlib import Path
from typing import Dict, Any, List


class InferenceTypeHintAgent:
    """
    Uses LLM inference to add accurate type hints to functions/methods.

    Why gated (not ungated):
    - Invokes SubAtomicEngine → API cost and rate limits
    - Higher risk of hallucinated types (mitigated by safety guardrail)
    - Best used in focused healing missions, not daily runs

    Strategy:
    - Extract functions without full type hints
    - Prompt SubAtomicEngine for precise annotations
    - Apply via AST + unparse (preserves formatting)
    """

    PROMPT_TEMPLATE = """
Add precise Python type hints to the following function/method.

Rules:
- Use concrete types when possible (List[str], Dict[str, int], etc.)
- Use from __future__ import annotations if needed
- Preserve all existing code, comments, and formatting
- Only modify type annotations (parameters and return)
- If uncertain, use Any from typing

Output ONLY the fully annotated function (no explanations, no markdown).

FUNCTION:
{code}
"""

    async def heal_violation(self, file_path: Path, ctx) -> Dict[str, Any]:
        """
        Per-file healing: invoke LLM for precise type inference.
        """
        if not getattr(ctx, "RUN_HIERARCHY_HEALING", False):
            return {"healed": False}  # Silent skip if not in surgery mode

        if not hasattr(ctx, "engine") or ctx.engine is None:
            print(f"   [!] InferenceTypeHintAgent: SubAtomicEngine not available")
            return {"healed": False}

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            # Find public functions/methods missing full hints
            targets: List[Dict] = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("_"):
                        continue
                    # Check if any param or return is missing
                    missing_param = any(arg.annotation is None for arg in node.args.args if arg.arg not in ("self", "cls"))
                    missing_return = node.returns is None
                    if missing_param or missing_return:
                        code_segment = ast.get_source_segment(source, node)
                        if code_segment:
                            targets.append({
                                "node": node,
                                "code": code_segment,
                                "lineno": node.lineno,
                            })

            if not targets:
                return {"healed": False}

            healed_count = 0
            lines = source.splitlines(keepends=True)

            for target in reversed(targets):  # Reverse to avoid line shifts
                prompt = self.PROMPT_TEMPLATE.format(code=target["code"])

                try:
                    # Use resilient_mutation for safety-wrapped inference
                    inferred_code = await ctx.engine.resilient_mutation(
                        file_path=str(file_path),
                        code=target["code"],
                        task=prompt,
                        round_num=1,
                        fission_active=False,
                    )

                    if isinstance(inferred_code, str):
                        inferred_code = inferred_code.strip()
                        # Extract code block if wrapped in LLM markdown
                        if inferred_code.startswith("```"):
                            inferred_code = "\n".join(inferred_code.splitlines()[1:-1])

                    # Replace in lines
                    start_idx = target["lineno"] - 1
                    end_idx = start_idx + target["code"].count("\n") + 1
                    original_block = "".join(lines[start_idx:end_idx])
                    
                    if inferred_code and inferred_code != original_block.strip():
                        # Preserve original leading whitespace/indentation profile
                        indent = lines[start_idx][:len(lines[start_idx]) - len(lines[start_idx].lstrip())]
                        indented_inferred = "\n".join(indent + l if i > 0 else l for i, l in enumerate(inferred_code.splitlines()))
                        lines[start_idx:end_idx] = [indented_inferred + "\n"]
                        healed_count += 1

                except Exception as e:
                    print(f"      [!] LLM inference failed for {file_path.name}:{target['lineno']}: {e}")
                    continue

            if healed_count > 0:
                new_content = "".join(lines)
                file_path.write_text(new_content, encoding="utf-8")
                message = f"Inferred {healed_count} precise type hint(s) via LLM"
                print(f"      [HEALED] {file_path.name}: {message}")
                ctx.report(self.__class__.__name__, 18, True, message)
                return {"healed": True, "details": message}

            return {"healed": False}

        except Exception as e:
            ctx.report(self.__class__.__name__, 18, False, f"Inference healing failed: {str(e)[:100]}")
            return {"healed": False}


# Factory for discovery
def get_inference_type_hint_agent():
    return InferenceTypeHintAgent()
