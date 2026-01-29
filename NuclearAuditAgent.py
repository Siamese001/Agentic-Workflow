#!/usr/bin/env python3
"""
Nuclear Audit: Comprehensive Agent Analysis for agentic_core/

Scans all agents in agentic_core/ and generates technical status table with:
- Agent Name (Full Class Name)
- Inheritance (SovereignBaseAgent verification)
- Mixin Verification (SubatomicTestingMixin, HealingStrategyMixin imports)
- heal() Signature (violation: dict parameter check)
- Primary Dependencies (agents/SDKs called)
- Namespace (SSOT folder verification)
- Status (Ready, Broken Import, Signature Mismatch, Stub)
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@dataclass
class AgentAuditResult:
    """Results from auditing a single agent."""
    agent_name: str
    file_path: str
    inheritance: str
    has_subatomic_testing: bool
    has_healing_strategy: bool
    heal_signature: str
    dependencies: List[str]
    namespace: str
    namespace_valid: bool
    status: str
    issues: List[str]

class NuclearAuditAgent:
    """Performs comprehensive nuclear audit of all agents."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agentic_core_dir = project_root / "agentic_core"
        
        # Load structure blueprint for namespace validation
        self.structure_blueprint = self._load_structure_blueprint()
        
        # Results storage
        self.results: List[AgentAuditResult] = []
        
    def _load_structure_blueprint(self) -> Dict:
        """Load structure blueprint for namespace validation."""
        blueprint_file = self.agentic_core_dir / "L5_safety" / "validators" / "structure_blueprint.py"
        try:
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract CORE_SUBFOLDER_MAP for namespace validation
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "CORE_SUBFOLDER_MAP":
                            return ast.literal_eval(node.value)
            return {}
        except Exception as e:
            logger.error(f"Failed to load structure blueprint: {e}")
            return {}
    
    def _find_agent_files(self) -> List[Path]:
        """Find all Python files containing agent classes."""
        agent_files = []
        for py_file in self.agentic_core_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Quick check for agent-like content
                if "class" in content and ("Agent" in content or "Mixin" in content):
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            if node.name.endswith("Agent") or "Mixin" in node.name:
                                agent_files.append(py_file)
                                break
            except Exception as e:
                logger.warning(f"Failed to parse {py_file}: {e}")
        
        return sorted(set(agent_files))
    
    def _analyze_class(self, file_path: Path, class_node: ast.ClassDef) -> AgentAuditResult:
        """Analyze a single agent class."""
        class_name = class_node.name
        rel_path = file_path.relative_to(self.project_root)
        
        # Initialize result
        result = AgentAuditResult(
            agent_name=class_name,
            file_path=str(rel_path),
            inheritance="Unknown",
            has_subatomic_testing=False,
            has_healing_strategy=False,
            heal_signature="Not found",
            dependencies=[],
            namespace=str(rel_path.parent),
            namespace_valid=False,
            status="Ready",
            issues=[]
        )
        
        # Analyze inheritance
        inheritance_chain = []
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                inheritance_chain.append(base.id)
            elif isinstance(base, ast.Attribute):
                inheritance_chain.append(ast.unparse(base))
        result.inheritance = ", ".join(inheritance_chain)
        
        # Check for SovereignBaseAgent inheritance
        has_sovereign = any("SovereignBaseAgent" in base for base in inheritance_chain)
        if not has_sovereign and not class_name.endswith("Mixin"):
            result.issues.append("Missing SovereignBaseAgent inheritance")
            result.status = "Broken Import"
        
        # Check for mixin imports
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result.has_subatomic_testing = "SubatomicTestingMixin" in content
            result.has_healing_strategy = "HealingStrategyMixin" in content
            
            # Analyze heal() method signature
            heal_methods = [node for node in class_node.body if isinstance(node, ast.FunctionDef) and node.name == "heal"]
            if heal_methods:
                heal_method = heal_methods[0]
                args = [arg.arg for arg in heal_method.args.args]
                if "violation" in args and "dict" in str(heal_method.args.args[1]) if len(heal_method.args.args) > 1 else False:
                    result.heal_signature = "heal(self, violation: dict)"
                else:
                    result.heal_signature = f"heal({', '.join(args)})"
                    if "violation" not in args:
                        result.issues.append("heal() method missing 'violation: dict' parameter")
                        result.status = "Signature Mismatch"
            elif has_sovereign:  # Should have heal method if inheriting from SovereignBaseAgent
                result.issues.append("Missing heal() method")
                result.status = "Signature Mismatch"
            
            # Extract dependencies
            imports = re.findall(r'from\s+([^\s]+)\s+import|import\s+([^\s]+)', content)
            for import_match in imports:
                module = import_match[0] or import_match[1]
                if "Agent" in module or any(x in module for x in ["sdk", "api", "external"]):
                    result.dependencies.append(module)
            
        except Exception as e:
            result.issues.append(f"File analysis error: {e}")
            result.status = "Broken Import"
        
        # Validate namespace
        namespace_parts = str(rel_path.parent).split('/')
        if len(namespace_parts) >= 2 and namespace_parts[0] == "agentic_core":
            if len(namespace_parts) >= 3:
                layer_folder = namespace_parts[2]
                subfolder = namespace_parts[3] if len(namespace_parts) > 3 else None
                
                # Check if layer is in blueprint
                if layer_folder in self.structure_blueprint:
                    valid_subfolders = self.structure_blueprint[layer_folder]
                    if subfolder is None or subfolder in valid_subfolders:
                        result.namespace_valid = True
                    else:
                        result.issues.append(f"Invalid subfolder '{subfolder}' in layer '{layer_folder}'")
                        result.status = "Signature Mismatch"
                else:
                    result.issues.append(f"Unknown layer '{layer_folder}'")
                    result.status = "Signature Mismatch"
            else:
                result.issues.append("Insufficient namespace depth")
                result.status = "Signature Mismatch"
        
        # Check for stub status
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "TODO" in content or "FIXME" in content or "STUB" in content.upper():
                if result.status == "Ready":
                    result.status = "Stub"
                    result.issues.append("Contains TODO/FIXME/STUB markers")
            
            # Check for pass-only methods
            if re.search(r'def\s+\w+\s*\([^)]*\)\s*:\s*pass', content):
                if result.status == "Ready":
                    result.status = "Stub"
                    result.issues.append("Contains pass-only methods")
                    
        except Exception:
            pass
        
        return result
    
    def run_audit(self) -> List[AgentAuditResult]:
        """Run comprehensive nuclear audit."""
        print("Starting Nuclear Audit of agentic_core/...")
        
        agent_files = self._find_agent_files()
        print(f"Found {len(agent_files)} agent files to analyze")
        
        for file_path in agent_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if node.name.endswith("Agent") or "Mixin" in node.name:
                            result = self._analyze_class(file_path, node)
                            self.results.append(result)
                            
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
        
        print(f"Analyzed {len(self.results)} agent classes")
        return self.results
    
    def generate_markdown_table(self) -> str:
        """Generate comprehensive markdown status table."""
        if not self.results:
            return "No results found."
        
        # Sort by status (priority first) then by namespace
        priority_order = {"Broken Import": 0, "Signature Mismatch": 1, "Stub": 2, "Ready": 3}
        sorted_results = sorted(
            self.results,
            key=lambda x: (priority_order.get(x.status, 4), x.namespace, x.agent_name)
        )
        
        # Generate table header
        table = [
            "# Nuclear Audit Results: agentic_core/ Agent Technical Status\n",
            "Generated comprehensive analysis of all agents in agentic_core/ directory.\n",
            "## Summary Statistics\n",
            f"- **Total Agents**: {len(self.results)}",
            f"- **Ready**: {len([r for r in self.results if r.status == 'Ready'])}",
            f"- **Broken Import**: {len([r for r in self.results if r.status == 'Broken Import'])}",
            f"- **Signature Mismatch**: {len([r for r in self.results if r.status == 'Signature Mismatch'])}",
            f"- **Stub**: {len([r for r in self.results if r.status == 'Stub'])}",
            "",
            "## Detailed Technical Status Table\n",
            "| Agent Name | Inheritance | Mixin Verification | heal() Signature | Primary Dependencies | Namespace | Status | Issues |",
            "|------------|-------------|-------------------|------------------|-------------------|----------|--------|---------|"
        ]
        
        # Generate table rows
        for result in sorted_results:
            # Format mixins
            mixins = []
            if result.has_subatomic_testing:
                mixins.append("[OK] SubatomicTesting")
            if result.has_healing_strategy:
                mixins.append("[OK] HealingStrategy")
            mixins_str = ", ".join(mixins) if mixins else "[MISSING]"
            
            # Format dependencies
            deps_str = ", ".join(result.dependencies[:3])  # Limit to first 3
            if len(result.dependencies) > 3:
                deps_str += f" (+{len(result.dependencies)-3})"
            
            # Format namespace with validation indicator
            namespace_str = f"{result.namespace} {'[OK]' if result.namespace_valid else '[INVALID]'}"
            
            # Format status with indicator
            status_indicator = {
                "Ready": "[OK]",
                "Broken Import": "[CRITICAL]",
                "Signature Mismatch": "[WARNING]",
                "Stub": "[INFO]"
            }
            status_str = f"{status_indicator.get(result.status, '[UNKNOWN]')} {result.status}"
            
            # Highlight problematic rows
            row_prefix = "**" if result.status in ["Broken Import", "Signature Mismatch"] else ""
            row_suffix = "**" if result.status in ["Broken Import", "Signature Mismatch"] else ""
            
            issues_str = "; ".join(result.issues[:2])  # Limit to first 2 issues
            if len(result.issues) > 2:
                issues_str += f" (+{len(result.issues)-2})"
            
            table.append(
                f"| {row_prefix}{result.agent_name}{row_suffix} | "
                f"{result.inheritance} | "
                f"{mixins_str} | "
                f"{result.heal_signature} | "
                f"{deps_str} | "
                f"{namespace_str} | "
                f"{status_str} | "
                f"{issues_str} |"
            )
        
        # Add high-priority remediation section
        problematic = [r for r in self.results if r.status in ["Broken Import", "Signature Mismatch"]]
        if problematic:
            table.extend([
                "",
                "## High-Priority Remediation Targets",
                "",
                "The following agents require immediate attention:",
                ""
            ])
            
            for result in problematic:
                table.extend([
                    f"### **{result.agent_name}** ({result.status})",
                    f"- **File**: `{result.file_path}`",
                    f"- **Issues**: {'; '.join(result.issues)}",
                    f"- **Inheritance**: {result.inheritance}",
                    f"- **Namespace**: {result.namespace}",
                    ""
                ])
        
        return "\n".join(table)

def main():
    """Main entry point for nuclear audit."""
    project_root = Path.cwd()
    
    # Verify we're in the right directory
    if not (project_root / "agentic_core").exists():
        print("Error: Must be run from project root with agentic_core/ directory")
        return
    
    # Run audit
    auditor = NuclearAuditAgent(project_root)
    results = auditor.run_audit()
    
    # Generate and save report
    report = auditor.generate_markdown_table()
    
    # Save to file
    report_file = project_root / "NUCLEAR_AUDIT_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Nuclear audit complete! Report saved to: {report_file}")
    
    # Print summary
    broken = len([r for r in results if r.status == "Broken Import"])
    mismatch = len([r for r in results if r.status == "Signature Mismatch"])
    
    if broken > 0 or mismatch > 0:
        print(f"Found {broken} broken imports and {mismatch} signature mismatches - immediate attention required!")
    else:
        print("All agents passed basic validation!")

if __name__ == "__main__":
    main()
