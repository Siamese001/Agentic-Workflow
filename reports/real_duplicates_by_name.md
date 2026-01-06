# Real Duplicate Agents (By Name)
**Generated:** 2026-01-06 06:56:22
**Duplicate Agent Names:** 3
**Files to Delete:** 3

| Agent Name | Canonical Path | Duplicate Path | Rationale |
| --- | --- | --- | --- |
| DeadCodeDetectorAgent | `agentic_core\L5_safety\guardrails\DeadCodeDetectorAgent.py` | `agentic_core\utils\core_extensions\DeadCodeDetectorAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| FileManagerAgent | `agentic_core\L4_state\filesystem\FileManagerAgent.py` | `agentic_core\utils\core_extensions\FileManagerAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| PromptGovernorAgent | `agentic_core\L2_execution\ToolRegistry\PromptGovernorAgent.py` | `agentic_core\prompt_governance\rendering\PromptGovernorAgent.py` | Exact duplicate — likely copy-paste or migration artifact |

---

## Delete Commands

**IMPORTANT:** Review each file before deleting. Use diff to compare:
```bash
code --diff "canonical_path" "duplicate_path"
```

### Delete Duplicates
```bash
git rm "agentic_core\utils\core_extensions\DeadCodeDetectorAgent.py"
git rm "agentic_core\utils\core_extensions\FileManagerAgent.py"
git rm "agentic_core\prompt_governance\rendering\PromptGovernorAgent.py"
```
