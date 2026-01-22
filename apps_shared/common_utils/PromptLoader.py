"""
Dynamic Prompt Loader for Canon Validator Agents

Loads prompts from modularized markdown files based on agent role.
"""



class PromptLoader:
    """Loads and caches prompts from markdown files."""

    def __init__(self, prompts_dir: str | None = None):
        """Initialize prompt loader with base directory."""
        if prompts_dir is None:
            # Default to prompts/ directory at project root
            # Navigate from this file to project root
            project_root = Path(__file__).parent.parent
            self.prompts_dir = project_root / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)

        self._cache: dict[str, str] = {}
        self._global_constraints: str | None = None

    def load_global_constraints(self) -> str:
        """Load global constraints that apply to all agents."""
        if self._global_constraints is not None:
            return self._global_constraints

        constraints_path = self.prompts_dir / "global" / "constraints.md"
        if constraints_path.exists():
            self._global_constraints = constraints_path.read_text(encoding="utf-8")
        else:
            self._global_constraints = ""

        return self._global_constraints

    def load_specialist_prompt(self, agent_role: str) -> str:
        """
        Load specialist prompt for a specific agent role.

        Args:
            agent_role: Name of the agent (e.g., 'healer_agent', 'system_architect')

        Returns:
            Specialist prompt content or empty string if not found
        """
        # Check cache first
        if agent_role in self._cache:
            return self._cache[agent_role]

        # Load from file
        specialist_path = self.prompts_dir / "specialists" / f"{agent_role}.md"
        if specialist_path.exists():
            content = specialist_path.read_text(encoding="utf-8")
            self._cache[agent_role] = content
            return content

        return ""

    def build_full_prompt(
        self,
        agent_role: str,
        task: str,
        code: str,
        original_line_count: int,
        lesson_learned: str = "",
    ) -> str:
        """
        Build complete prompt combining global constraints and specialist instructions.

        Args:
            agent_role: Name of the agent
            task: Specific task description
            code: Code to be fixed
            original_line_count: Number of lines in original file
            lesson_learned: Optional lesson from previous failure

        Returns:
            Complete prompt ready for LLM
        """
        # Load components
        global_constraints = self.load_global_constraints()
        specialist_prompt = self.load_specialist_prompt(agent_role)

        # Build prompt sections
        sections = []

        # Task header
        sections.append(f"Task: {task}")

        # Specialist instructions
        if specialist_prompt:
            sections.append(specialist_prompt)

        # Global constraints with line count
        if global_constraints:
            # Replace placeholder with actual line count
            constraints_with_count = global_constraints.replace(
                "{original_line_count}", str(original_line_count)
            )
            constraints_with_count = constraints_with_count.replace(
                "{int(original_line_count * 0.1)}", str(int(original_line_count * 0.1))
            )
            sections.append(constraints_with_count)

        # Lesson learned from previous failure
        if lesson_learned:
            sections.append(
                f"\n📚 LESSON LEARNED FROM PREVIOUS ATTEMPT:\n{lesson_learned}\nApply this lesson to your current fix. Start fresh with the original file.\n"
            )

        # Code to fix
        sections.append(f"\n{code}")

        return "\n\n".join(sections)

    def get_available_specialists(self) -> list[str]:
        """Get list of available specialist prompts."""
        specialists_dir = self.prompts_dir / "specialists"
        if not specialists_dir.exists():
            return []

        return [f.stem for f in specialists_dir.glob("*.md")]

    def reload_cache(self):
        """Clear cache to force reload of prompts."""
        self._cache.clear()
        self._global_constraints = None


# Global instance for easy access
_loader = PromptLoader()


def load_prompt_for_agent(
    agent_role: str, task: str, code: str, original_line_count: int, lesson_learned: str = ""
) -> str:
    """
    Convenience function to load complete prompt for an agent.

    Args:
        agent_role: Name of the agent (e.g., 'healer_agent')
        task: Specific task description
        code: Code to be fixed
        original_line_count: Number of lines in original file
        lesson_learned: Optional lesson from previous failure

    Returns:
        Complete prompt ready for LLM
    """
    return _loader.build_full_prompt(agent_role, task, code, original_line_count, lesson_learned)


def get_global_constraints() -> str:
    """Get global constraints that apply to all agents."""
    return _loader.load_global_constraints()


def get_specialist_prompt(agent_role: str) -> str:
    """Get specialist prompt for a specific agent role."""
    return _loader.load_specialist_prompt(agent_role)