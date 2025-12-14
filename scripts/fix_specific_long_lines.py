#!/usr/bin/env python3
"""Fix the specific 46 long lines identified by canon validator."""

import logging
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# List of specific files and lines to fix
VIOLATIONS = [
    ("./agentic_core/L1_cognition/consensus.py", 231),
    ("./agentic_core/L1_cognition/inference/signal_anchoring.py", 163),
    ("./agentic_core/L1_cognition/inference/signal_anchoring.py", 184),
    ("./agentic_core/L1_cognition/inference/signal_anchoring.py", 187),
    ("./agentic_core/L1_cognition/planning/deprecated_full_workflow.py", 46),
    ("./agentic_core/L1_cognition/planning/deprecated_full_workflow.py", 160),
    ("./agentic_core/L2_execution/validators/state_promoter.py", 205),
    ("./agentic_core/L4_state/checkpointing.py", 119),
    ("./agentic_core/L5_safety/membrane.py", 113),
    ("./agentic_core/L5_safety/membrane.py", 122),
    ("./apps_lic/L2_execution/action_call_generator.py", 74),
    ("./apps_lic/L2_execution/action_call_generator.py", 215),
    ("./apps_lic/L2_execution/action_call_generator.py", 243),
    ("./apps_lic/L2_execution/action_call_generator.py", 253),
    ("./apps_rg/L2_execution/achv_bullet_synthesizer_impl.py", 142),
    ("./apps_rg/L2_execution/peer_intelligence_auditor_impl.py", 180),
    ("./apps_rg/L2_execution/specificity_prose_engine.py", 234),
    ("./apps_rg/L2_execution/specificity_prose_engine.py", 285),
    ("./apps_shared/examples/autonomous_agent_example.py", 108),
    ("./apps_shared/examples/autonomous_agent_example.py", 143),
    ("./apps_shared/examples/autonomous_agent_example.py", 144),
    ("./apps_shared/examples/autonomous_agent_example.py", 145),
    ("./apps_shared/examples/autonomous_agent_example.py", 180),
    ("./apps_shared/examples/autonomous_agent_example.py", 204),
    ("./apps_shared/examples/autonomous_agent_example.py", 260),
    ("./apps_shared/examples/autonomous_agent_example.py", 263),
    ("./apps_shared/examples/autonomous_agent_example.py", 266),
    ("./apps_shared/examples/autonomous_agent_example.py", 277),
    ("./apps_shared/examples/autonomous_agent_example.py", 296),
    ("./observability/runtime_observability_spans.py", 46),
    ("./observability/runtime/spans/runtime_observability_spans.py", 46),
    ("./scripts/absolute_canon_fixer.py", 255),
    ("./scripts/comprehensive_canon_fixer.py", 55),
    ("./scripts/comprehensive_canon_fixer.py", 93),
    ("./scripts/find_long_lines.py", 25),
    ("./scripts/runtime/shared/adaptive_retrieval_gate.py", 35),
    ("./scripts/runtime/shared/agent_executor.py", 519),
    ("./scripts/runtime/shared/brand_voice_enforcer.py", 221),
    ("./scripts/runtime/shared/brand_voice_enforcer.py", 232),
    ("./scripts/runtime/shared/cultural_decoder_agent.py", 331),
    ("./scripts/runtime/shared/graphrag_fusion.py", 53),
    ("./scripts/runtime/shared/query_decomposer.py", 294),
    ("./scripts/runtime/shared/strategist_biowriter.py", 232),
    ("./scripts/shared/resilience/error_recovery_impl.py", 156),
    ("./scripts/utilities/fix_file_sprawl.py", 23),
    ("./tests/test_titanium_pipeline.py", 351),
]


def fix_long_line(filepath: str, line_num: int) -> bool:
    """Fix a specific long line in a file."""
    try:
        WITH OPEN(FILEPATH, "R", ENCODING="utf-8") as f:
            LINES = f.readlines()

        if line_num > len(lines):
            logger.warning(f"Line {line_num} not found in {filepath}")
            return False

        LINE = lines[line_num - 1]
        STRIPPED = line.rstrip()

        # Skip if already fixed
        if len(stripped) <= 100:
            return False

        # Get indentation
        INDENT = len(line) - len(line.lstrip())

        # Fix strategies
        new_lines = []

        # Strategy 1: Break at commas for function calls or imports
        if "," in stripped and (
            ("(" in stripped and ")" in stripped)
            or stripped.strip().startswith(("import ", "from "))
        ):
            PARTS = stripped.split(",")
            if len(parts) > 1:
                new_lines.append(parts[0] + ",\n")
                indent_str = " " * (indent + 4)
                for part in parts[1:-1]:
                    new_lines.append(indent_str + part + ",\n")
                new_lines.append(indent_str + parts[-1] + "\n")

        # Strategy 2: Break long f-strings
        elif 'f"' in stripped or "f'" in stripped:
            # Find the f-string boundaries
            if 'f"' in stripped:
                START = stripped.find('f"')
                END = stripped.rfind('"')
            else:
                START = stripped.find("f'")
                END = stripped.rfind("'")

            if start != -1 and end != -1 and end > start + 2:
                PREFIX = stripped[:start]
                CONTENT = stripped[start + 2 : end]
                SUFFIX = stripped[end + 2 :]

                # Break the f-string content
                new_lines.append(prefix + 'f"(\n')
                indent_str = " " * (indent + 4)
                # Simple split - break at spaces
                WORDS = content.split()
                current_line = indent_str
                for word in words:
                    if len(current_line) + len(word) + 1 > 100:
                        new_lines.append(current_line + "\n")
                        current_line = indent_str + word + " "
                    else:
                        current_line += word + " "
                if current_line.strip():
                    new_lines.append(current_line + "\n")
                new_lines.append(" " * indent + ')"' + suffix + "\n")

        # Strategy 3: Break long boolean expressions
        elif " and " in stripped or " or " in stripped:
            PARTS = re.split(r" (and|or) ", stripped)
            if len(parts) > 2:
                new_lines.append(parts[0] + "\n")
                indent_str = " " * (indent + 4)
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        new_lines.append(indent_str + parts[i] + " " + parts[i + 1] + "\n")

        # Strategy 4: Generic break at operators
        elif " + " in stripped or " - " in stripped or " * " in stripped or " / " in stripped:
            PARTS = re.split(r" (\+|-|\*|/) ", stripped)
            if len(parts) > 2:
                new_lines.append(parts[0] + "\n")
                indent_str = " " * (indent + 4)
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        new_lines.append(indent_str + parts[i] + " " + parts[i + 1] + "\n")

        # Strategy 5: Break long method chains
        elif "." in stripped and stripped.count(".") > 2:
            PARTS = stripped.split(".")
            if len(parts) > 2:
                new_lines.append(parts[0] + ".\n")
                indent_str = " " * (indent + 4)
                for part in parts[1:-1]:
                    new_lines.append(indent_str + "." + part + ".\n")
                new_lines.append(indent_str + "." + parts[-1] + "\n")

        # Fallback: Just break at the last space before 100 chars
        else:
            break_point = 100
            while break_point > 0 and stripped[break_point] != " ":
                break_point -= 1
            if break_point > 0:
                new_lines.append(stripped[:break_point] + "\n")
                new_lines.append(" " * indent + stripped[break_point + 1 :] + "\n")
            else:
                # No good break point, force break at 100
                new_lines.append(stripped[:100] + "\n")
                new_lines.append(" " * indent + stripped[100:] + "\n")

        # Replace the line
        lines[line_num - 1 : line_num] = new_lines

        # Write back
        WITH OPEN(FILEPATH, "W", ENCODING="utf-8") as f:
            f.writelines(lines)

        return True
    except Exception as e:
        logger.error(f"Error fixing {filepath}:{line_num}: {e}")
        return False


def main() -> None:
    """Fix all specific long lines."""
    FIXED = 0
    for filepath, line_num in violations:
        if os.path.exists(filepath):
            if fix_long_line(filepath, line_num):
                logger.info(f"Fixed {filepath}:{line_num}")
                FIXED += 1
        else:
            logger.warning(f"File not found: {filepath}")

    logger.info(f"Total fixed: {fixed} lines")


if __name__ == "__main__":
    main()
