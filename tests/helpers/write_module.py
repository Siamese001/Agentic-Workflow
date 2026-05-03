"""
Module content generators for testing FCA classification.

Provides functions to generate Python module content with specific
characteristics for testing AST extraction and classification logic.
"""

from __future__ import annotations

def agent_module(agent_name: str, base_class: str = "SovereignBaseAgent") -> str:
    """Generate a module containing an Agent class."""
    return f'''"""Agent module for {agent_name}."""

class {agent_name}({base_class}):
    """A concrete agent class."""

    def execute(self):
        pass
'''


def validator_module(validator_name: str) -> str:
    """Generate a module containing a Validator class."""
    return f'''"""Validator module for {validator_name}."""

class {validator_name}:
    """A validator class."""

    def validate(self, data):
        return True
'''


def manager_module(manager_name: str, signals: str = "cache") -> str:
    """Generate a Manager module with specific signals."""
    signal_map = {
        "cache": "self.cache = {}",
        "state": "self.state = {}",
        "workflow": "self.workflow = []",
        "dag": "self.dag = None",
        "subprocess": "import subprocess",
        "tool": "self.tool_registry = {}",
    }
    signal_code = signal_map.get(signals, "pass")
    return f'''"""Manager module for {manager_name}."""

class {manager_name}:
    """A manager class with {signals} signals."""

    def __init__(self):
        {signal_code}
'''


def script_module(with_main: bool = True, with_class: bool = False) -> str:
    """Generate a script-like module."""
    content = '''"""Script module."""

def main():
    print("Running script")

'''
    if with_class:
        content += '''
class SomeClass:
    """A class that shouldn't be in scripts."""
    pass

'''
    if with_main:
        content += """if __name__ == "__main__":
    main()
"""
    return content


def types_module(with_agent: bool = False) -> str:
    """Generate a types module, optionally with embedded Agent."""
    content = '''"""Types module."""
from dataclasses import dataclass

@dataclass
class SomeType:
    value: str
'''
    if with_agent:
        content += '''

class EmbeddedAgent:
    """An agent that shouldn't be in types/."""
    def execute(self):
        pass
'''
    return content


def subprocess_module() -> str:
    """Generate a module that uses subprocess."""
    return '''"""Module using subprocess."""
import subprocess

def run_command(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout
'''


def safe_subprocess_wrapper() -> str:
    """Generate a safe subprocess wrapper (L5 allowed)."""
    return '''"""Safe subprocess handler for L5 safety layer."""
import subprocess
from typing import Sequence

def safe_subprocess_run(cmd: Sequence[str], **kwargs) -> subprocess.CompletedProcess:
    """Execute subprocess with safety checks."""
    # Validate command
    if not cmd:
        raise ValueError("Empty command")
    # Execute with restrictions
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
'''


def syntax_error_module() -> str:
    """Generate a module with syntax errors."""
    return '''"""Module with syntax error."""
def broken_function(
    # Missing closing paren
'''


def protocol_module(name: str) -> str:
    """Generate a Protocol interface (not a concrete Agent)."""
    return f'''"""Protocol interface module."""
from typing import Protocol

class {name}(Protocol):
    """A protocol interface."""
    def execute(self) -> None:
        ...
'''


def nested_lcd_module() -> str:
    """Generate a module in a nested LCD location."""
    return '''"""Module in nested LCD location."""

def helper():
    pass
'''
