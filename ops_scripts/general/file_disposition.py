"""
File: C:/Git/Agentic-Workflow/scripts/ast_disposition_analyzer.py
Context: New diagnostic tool to perform zero-loss analysis of common_utils using AST to identify hidden Agents based on imports, class inheritance, and decorator usage.
"""
import ast
import os
from dataclasses import dataclass
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

TARGET_DIR = 'C:\\Git\\Agentic-Workflow\\apps_shared\\common_utils'

@dataclass
class FileDisposition:
    filepath: str
    is_agent: bool
    confidence: str
    signals: list[str]

class AgentVisitor(ast.NodeVisitor):

    def __init__(self):
        self.is_agent = False
        self.signals = []
        self.agent_imports = {'langchain', 'openai', 'anthropic', 'crewai', 'autogen'}
        self.agent_bases = {'BaseAgent', 'Agent', 'Chain', 'LLMChain'}
        self.agent_decorators = {'tool', 'action'}

    def visit_Import(self, node):
        for alias in node.names:
            if any(imp in alias.name for imp in self.agent_imports):
                self.is_agent = True
                self.signals.append(f'Import detected: {alias.name}')
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and any(imp in node.module for imp in self.agent_imports):
            self.is_agent = True
            self.signals.append(f'From-Import detected: {node.module}')
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in self.agent_bases:
                self.is_agent = True
                self.signals.append(f'Inheritance detected: {base.id}')
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in self.agent_decorators:
                self.is_agent = True
                self.signals.append(f'Decorator detected: @{decorator.id}')
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and (decorator.func.id in self.agent_decorators):
                self.is_agent = True
                self.signals.append(f'Decorator call detected: @{decorator.func.id}')
        self.generic_visit(node)

def analyze_directory(directory: str) -> list[FileDisposition]:
    results = []
    # guardian: allow-path-string
    if not os.path.exists(directory):
        print(f'Directory not found: {directory}')
        return []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if not file.endswith('.py'):
                continue
            full_path = Path(root) / file
            with open(full_path, encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                    visitor = AgentVisitor()
                    visitor.visit(tree)
                    results.append(FileDisposition(filepath=full_path, is_agent=visitor.is_agent, confidence='HIGH' if visitor.signals else 'LOW', signals=visitor.signals))
                except Exception as e:
                    raise
                    results.append(FileDisposition(filepath=full_path, is_agent=False, confidence='ERROR', signals=[f'Parse Error: {str(e)}']))
    return results

def generate_report(results: list[FileDisposition]):
    print(f"{'DISPOSITION':<12} | {'FILE PATH':<60} | {'SIGNALS'}")
    print('-' * 100)
    for r in results:
        disp = 'MOVE' if r.is_agent else 'STAY'
        rel_path = r.filepath.replace('C:\\Git\\Agentic-Workflow', '...')
        signals = ', '.join(r.signals[:2])
        if r.is_agent:
            print(f'!! {disp:<9} | {rel_path:<60} | {signals}')
        else:
            print(f'   {disp:<9} | {rel_path:<60} | -')
if __name__ == '__main__':
    print(f'Scanning {TARGET_DIR} for Agent Contamination...')
    data = analyze_directory(TARGET_DIR)
    generate_report(data)
