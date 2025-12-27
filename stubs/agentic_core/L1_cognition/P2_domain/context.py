"""Stub for ValidationContext."""
from typing import Dict, List, Set, Any

class ValidationContext:
    """Stub validation context for agentic workflow."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.modified_files: Set[str] = set()
        self.dependencies: Dict[str, List[str]] = {}
        self.signals: Set[str] = set()
        self.instructions: List[str] = []
        self.results: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
        self._streamer_initialized: bool = False
    
    def add_error(self, error: str):
        """Add an error to the context."""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a warning to the context."""
        self.warnings.append(warning)
    
    def add_modified_file(self, file_path: str):
        """Track a modified file."""
        self.modified_files.add(file_path)
    
    def add_dependency(self, file_path: str, dependencies: List[str]):
        """Add dependencies for a file."""
        self.dependencies[file_path] = dependencies
    
    def inject_instruction(self, source_agent: str, instruction: str):
        """Add a guiding hint to the blackboard for downstream agents."""
        self.instructions.append(f"[{source_agent}] {instruction}")
    
    def report_property_failure(self, func_name: str, counter_example: str):
        """Reports a Hypothesis property violation."""
        self.signals.add("PROPERTY_VIOLATION")
        self.inject_instruction("Sherlock", f"Property invariant failed in {func_name}. Hypothesis found edge case: {counter_example}. Fix logic immediately.")
    
    def report(self, agent_name: str, key: int, passed: bool, details: list):
        """Report results to blackboard."""
        self.results[key] = {"passed": passed, "details": details, "agent": agent_name}
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the full dependency graph."""
        return self.dependencies.copy()
    
    def has_errors(self) -> bool:
        """Check if context has any errors."""
        return len(self.errors) > 0
    
    def clear(self):
        """Clear all context data."""
        self.errors.clear()
        self.warnings.clear()
        self.modified_files.clear()
        self.dependencies.clear()
        self.signals.clear()
        self.instructions.clear()
        self.results.clear()
    
    def is_valid(self) -> bool:
        return len(self.errors) == 0
