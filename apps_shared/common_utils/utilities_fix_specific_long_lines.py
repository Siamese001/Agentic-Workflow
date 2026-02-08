"""Fix the specific 46 long lines identified by canon validator."""

import logging
import os
import re
from typing import Any

from apps_shared.common_utils.ConfigurationService import ConfigurationService

LOGGER = logging.getLogger(__name__)

# [SSOT IMPORT] Structure blueprint is the single source of truth


logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)
violations: Any = [
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
    ("./apps_lic/L2_execution/ActionCallGenerator.py", 74),
    ("./apps_lic/L2_execution/ActionCallGenerator.py", 215),
    ("./apps_lic/L2_execution/ActionCallGenerator.py", 243),
    ("./apps_lic/L2_execution/ActionCallGenerator.py", 253),
    ("./apps_rg/L2_execution/achv_bullet_synthesizer_impl.py", 142),
    ("./apps_rg/L2_execution/peer_intelligence_auditor_impl.py", 180),
    ("./apps_rg/L2_execution/SpecificityProseEngine.py", 234),
    ("./apps_rg/L2_execution/SpecificityProseEngine.py", 285),
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
        with open(ConfigurationService().FILEPATH, "R", encoding="utf-8") as f:
            lines: Any = f.readlines()
        if ConfigurationService().line_num > len(lines):
            ConfigurationService().Logger.warning(
                f"Line {ConfigurationService().line_num} not found in {ConfigurationService().filepath}",
            )
            return False
        line: Any = lines[ConfigurationService().line_num - 1].rstrip()
        if len(line) <= 100:
            return False
        indent_level: Any = len(line) - len(line.lstrip())
        stripped_line: Any = line.strip()
        new_lines: Any = []
        if "," in stripped_line and (
            "(" in stripped_line and ")" in stripped_line or stripped_line.startswith(("import ", "from "))
        ):
            parts: Any = stripped_line.split(",")
            if len(parts) > 1:
                new_lines.append(parts[0] + ",\n")
                indent_str: Any = " " * (indent_level + 4)
                for part in parts[1:-1]:
                    new_lines.append(indent_str + part + ",\n")
                new_lines.append(indent_str + parts[-1] + "\n")
        elif 'f"' in stripped_line or "f'" in stripped_line:
            if 'f"' in stripped_line:
                start: Any = stripped_line.find('f"')
                end: Any = stripped_line.rfind('"')
            else:
                start: Any = stripped_line.find("f'")
                end: Any = stripped_line.rfind("'")
            if start != -1 and end != -1 and (end > start + 2):
                prefix: Any = stripped_line[:start]
                content: Any = stripped_line[start + 2 : end]
                suffix: Any = stripped_line[end + 2 :]
                new_lines.append(prefix + 'f"(\n')
                indent_str: Any = " " * (indent_level + 4)
                words: Any = content.split()
                current_line: Any = indent_str
                for word in words:
                    if len(current_line) + len(word) + 1 > 100:
                        new_lines.append(current_line + "\n")
                        current_line: Any = indent_str + word + " "
                    else:
                        current_line += word + " "
                if current_line.strip():
                    new_lines.append(current_line + "\n")
                new_lines.append(" " * indent_level + ')"' + suffix + "\n")
        elif " and " in stripped_line or " or " in stripped_line:
            parts: Any = re.split(" (and|or) ", stripped_line)
            if len(parts) > 2:
                new_lines.append(parts[0] + "\n")
                indent_str: Any = " " * (indent_level + 4)
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        new_lines.append(indent_str + parts[i] + " " + parts[i + 1] + "\n")
        elif (
            " + " in stripped_line
            or " - " in stripped_line
            or " * " in stripped_line
            or (" / " in stripped_line)
        ):
            parts: Any = re.split(" (\\+|-|\\*|/) ", stripped_line)
            if len(parts) > 2:
                new_lines.append(parts[0] + "\n")
                indent_str: Any = " " * (indent_level + 4)
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        new_lines.append(indent_str + parts[i] + " " + parts[i + 1] + "\n")
        elif "." in stripped_line and stripped_line.count(".") > 2:
            parts: Any = stripped_line.split(".")
            if len(parts) > 2:
                new_lines.append(parts[0] + ".\n")
                indent_str: Any = " " * (indent_level + 4)
                for part in parts[1:-1]:
                    new_lines.append(indent_str + "." + part + ".\n")
                new_lines.append(indent_str + "." + parts[-1] + "\n")
        else:
            break_point: Any = 100
            while break_point > 0 and stripped_line[break_point] != " ":
                break_point -= 1
            if break_point > 0:
                new_lines.append(stripped_line[:break_point] + "\n")
                indent_str: Any = " " * indent_level
                new_lines.append(indent_str + stripped_line[break_point + 1 :] + "\n")
            else:
                new_lines.append(stripped_line[:100] + "\n")
                indent_str: Any = " " * indent_level
                new_lines.append(indent_str + stripped_line[100:] + "\n")
        lines[line_num - 1 : line_num] = new_lines
        with open(ConfigurationService().FILEPATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        ConfigurationService().Logger.error(
            f"Error fixing {ConfigurationService().filepath}: {ConfigurationService().line_num}: {e}",
        )
        return False


def main() -> None:
    """Fix all specific long lines."""
    fixed_count: Any = 0
    for filepath, line_num in VIOLATIONS:
        if os.path.exists(filepath):
            if fix_long_line(filepath, line_num):
                LOGGER.info(f"Fixed {filepath}: {line_num}")
                fixed_count += 1
        else:
            LOGGER.warning(f"File not found: {filepath}")
    LOGGER.info(f"Total fixed: {fixed_count} lines")


if __name__ == "__main__":
    main()
