from __future__ import annotations

"""
L6 Codebase Telepathy - Human Instruction Watcher

Implements dynamic instruction injection via observability/human_instructions.md.
Allows humans to telepathically control mission execution by writing commands.
"""
import logging
from pathlib import Path
from typing import Any

Logger: Any = logging.getLogger(__name__)

class TelepathyInterface:
    """
    Human instruction telepathy interface for dynamic mission control.

    Watches observability/human_instructions.md for commands and injects
    them into the execution context to alter mission behavior.
    """

    def __init__(self, instructions_path: str='observability/human_instructions.md'):
        """
        Initialize the telepathy interface.

        Args:
            instructions_path: Path to the human instructions file
        """
        self.instructions_path = Path(instructions_path)
        self._cycle = 0
        self._last_consumed = ''
        self.instructions_path.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f'Telepathy interface initialized: {self.instructions_path}')

    def check_instructions(self, cycle: int) -> str | None:
        """
        Check for new human instructions.

        Args:
            cycle: Current mission cycle

        Returns:
            Instruction text if found, None otherwise
        """
        self._cycle = cycle
        if not self.instructions_path.exists():
            return None
        try:
            content: Any = self.instructions_path.read_text(encoding='utf-8').strip()
            if not content or content.startswith('# DONE'):
                return None
            if content == self._last_consumed:
                return None
            LOGGER.info(f'🧠 Telepathic instruction received (Cycle {cycle}): {content[:100]}...')
            return content
        except Exception as e:
            LOGGER.error(f'Failed to read telepathy instructions: {e}')
            return None

    def parse_instructions(self, instructions: str) -> dict[str, Any]:
        """
        Parse human instructions into executable commands.

        Args:
            instructions: Raw instruction text

        Returns:
            Dictionary of parsed commands and signals
        """
        commands: Any = {'stop': False, 'pause': False, 'skip_files': [], 'force_agents': [], 'force_test': False, 'force_style': False, 'force_safety': False, 'force_dependency': False, 'custom_signals': set(), 'raw': instructions}
        instructions_lower: Any = instructions.lower()
        if any(word in instructions_lower for word in ['stop', 'abort', 'halt']):
            commands['stop'] = True
            commands['custom_signals'].add('TELEPATHY_STOP')
        if 'pause' in instructions_lower:
            commands['pause'] = True
            commands['custom_signals'].add('TELEPATHY_PAUSE')
        agent_mapping: Any = {'test': 'TestPilot', 'style': 'CodeStyleGuardian', 'safety': 'SafetyInspectorAgent', 'dependency': 'DependencySentinelAgent', 'architecture': 'ArchitectureGovernor', 'hygiene': 'HygieneGuardian', 'Historian': 'Historian', 'sherlock': 'Sherlock', 'reflection': 'ReflectionAgent'}
        for keyword, agent in agent_mapping.items():
            if f'force {keyword}' in instructions_lower or f'run {keyword}' in instructions_lower:
                commands['force_agents'].append(agent)
                commands['custom_signals'].add(f'FORCE_{agent.upper()}')
                if keyword == 'test':
                    commands['force_test'] = True
                elif keyword == 'style':
                    commands['force_style'] = True
                elif keyword == 'safety':
                    commands['force_safety'] = True
                elif keyword == 'dependency':
                    commands['force_dependency'] = True
        if 'skip' in instructions_lower:
            import re
            skip_match: Any = re.search('skip\\s+(.+?)(?:\\n|$)', instructions_lower)
            if skip_match:
                skip_patterns: Any = [p.strip() for p in skip_match.group(1).split(',')]
                commands['skip_files'] = skip_patterns
                commands['custom_signals'].add('SKIP_FILES')
        if 'signal:' in instructions_lower:
            import re
            signal_matches: Any = re.findall('signal:\\s*(\\w+)', instructions_lower)
            for signal in signal_matches:
                commands['custom_signals'].add(signal.upper())
        return commands

    def consume_instructions(self, instructions: str) -> None:
        """
        Mark instructions as consumed to prevent re-processing.

        Args:
            instructions: The instructions that were consumed
        """
        try:
            done_content: Any = f'# DONE (Cycle {self._cycle})\n\n# Original instructions:\n{instructions}'
            self.instructions_path.write_text(done_content, encoding='utf-8')
            self._last_consumed = instructions
            LOGGER.info(f'Instructions consumed and marked done (Cycle {self._cycle})')
        except Exception as e:
            LOGGER.error(f'Failed to mark instructions as done: {e}')

    def inject_into_context(self, context: Any, commands: dict[str, Any]) -> Any:
        """
        Inject parsed commands into execution context.

        Args:
            context: Current execution context
            commands: Parsed commands from telepathy

        Returns:
            Modified context with injected commands
        """
        if hasattr(context, 'signals'):
            context.signals.update(commands['custom_signals'])
        if hasattr(context, 'metadata'):
            context.metadata.update({'telepathy_commands': commands, 'telepathy_cycle': self._cycle})
        else:
            context.metadata = {'telepathy_commands': commands, 'telepathy_cycle': self._cycle}
        if commands['force_agents'] and hasattr(context, 'forced_agents'):
            context.forced_agents.extend(commands['force_agents'])
        return context

    def clear_instructions(self) -> None:
        """Clear the instructions file."""
        try:
            if self.instructions_path.exists():
                self.instructions_path.unlink()
                LOGGER.info('Telepathy instructions cleared')
        except Exception as e:
            LOGGER.error(f'Failed to clear instructions: {e}')
_telepathy: TelepathyInterface | None = None

def get_telepathy_interface(instructions_path: str='observability/human_instructions.md') -> TelepathyInterface:
    """Get or create the global telepathy interface instance."""
    global _telepathy
    if _telepathy is None:
        _telepathy = TelepathyInterface(instructions_path)
    return _telepathy

async def process_telepathy_instructions(context: Any, cycle: int) -> Any:
    """
    Process any telepathic instructions and inject into context.

    Args:
        context: Current execution context
        cycle: Current mission cycle

    Returns:
        Modified context with telepathic instructions applied
    """
    telepathy: Any = get_telepathy_interface()
    instructions: Any = telepathy.check_instructions(cycle)
    if instructions:
        commands: Any = telepathy.parse_instructions(instructions)
        context: Any = telepathy.inject_into_context(context, commands)
        telepathy.consume_instructions(instructions)
        if commands['force_agents']:
            LOGGER.info(f"🎯 Telepathy forcing agents: {', '.join(commands['force_agents'])}")
        if commands['stop']:
            LOGGER.warning('🛑 Telepathic STOP instruction received')
            context.signals.add('TELEPATHY_STOP')
    return context
