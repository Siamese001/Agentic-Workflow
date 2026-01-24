#!/usr/bin/env python3
"""
AST-Based Archive Recovery Auditor
Scans archive directories, fingerprints logic signatures, and identifies unique candidates for apps_rg migration.
"""

import ast
import hashlib
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants
ARCHIVE_ROOTS = [
    r"C:\Git\Agentic-Workflow\archives\Reachout Engine Archive",
    r"C:\Git\Agentic-Workflow\archives\resume_gen_json"
]
TARGET_ROOT = Path(r"C:\Git\Agentic-Workflow\apps_rg")
OUTPUT_JSON = TARGET_ROOT / "RG_ARCHIVE_RECOVERY_PLAN.json"

@dataclass
class LogicSignature:
    """Represents a unique code block (function or class)."""
    name: str
    type: str  # 'class' or 'function'
    content_hash: str
    line_count: int
    is_stateful: bool = False
    docstring: str = ""

@dataclass
class FileAudit:
    """Audit result for a single file."""
    path: str
    signatures: List[LogicSignature] = field(default_factory=list)
    classification: str = "unknown"  # Engine, Tool, Type, Legacy
    redundancy_score: float = 0.0    # 0.0 (Unique) to 1.0 (Fully Redundant)
    target_destination: Optional[str] = None
    refactor_notes: List[str] = field(default_factory=list)

class LogicHasher(ast.NodeVisitor):
    """AST Visitor to extract and hash logic blocks."""
    def __init__(self):
        self.signatures = []

    def _normalize_and_hash(self, node):
        """Strip docstrings/comments and hash the AST structure."""
        # Use ast.dump to capture structure, excluding attributes like line numbers
        content_to_hash = ast.dump(node, include_attributes=False)
        return hashlib.md5(content_to_hash.encode('utf-8')).hexdigest()

    def visit_ClassDef(self, node):
        # Heuristic: Stateful if it has init or execution methods
        is_stateful = any(n.name in ['__init__', 'execute', 'run', 'process', 'act'] 
                         for n in node.body if isinstance(n, ast.FunctionDef))
        
        # Heuristic: Type if it inherits from Enum/BaseModel
        bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
        is_type = any(b in ['Enum', 'BaseModel', 'TypedDict'] for b in bases)

        sig_type = 'type' if is_type else 'class'

        sig = LogicSignature(
            name=node.name,
            type=sig_type,
            content_hash=self._normalize_and_hash(node),
            line_count=node.end_lineno - node.lineno,
            is_stateful=is_stateful,
            docstring=ast.get_docstring(node) or ""
        )
        self.signatures.append(sig)
        # Don't visit children to avoid double counting methods inside classes for file-level redundancy
        # self.generic_visit(node) 

    def visit_FunctionDef(self, node):
        # Only capture top-level functions (visitor doesn't recurse into classes above due to commented generic_visit)
        sig = LogicSignature(
            name=node.name,
            type='function',
            content_hash=self._normalize_and_hash(node),
            line_count=node.end_lineno - node.lineno,
            docstring=ast.get_docstring(node) or ""
        )
        self.signatures.append(sig)

def scan_file(filepath: Path) -> Optional[FileAudit]:
    """Parse file and extract logic signatures."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        if not content.strip(): return None
        tree = ast.parse(content)
        hasher = LogicHasher()
        hasher.visit(tree)
        
        if not hasher.signatures:
            return None

        # Determine Classification
        classification = "unknown"
        sigs = hasher.signatures
        
        if any(s.type == 'type' for s in sigs):
            classification = "Type"
        elif any(s.type == 'class' and s.is_stateful for s in sigs):
            classification = "Engine"
        elif any(s.type == 'class' for s in sigs):
             # Classes without state are likely Tools or Configs
            classification = "Tool"
        elif any(s.type == 'function' for s in sigs):
            classification = "Tool"
            
        return FileAudit(
            path=str(filepath),
            signatures=sigs,
            classification=classification
        )
    except Exception as e:
        logger.warning(f"Skipping {filepath.name}: {e}")
        return None

def main():
    logger.info("Building Logic Fingerprint for apps_rg (Baseline)...")
    rg_signatures = set()
    
    # 1. Index current apps_rg
    if TARGET_ROOT.exists():
        for py_file in TARGET_ROOT.rglob("*.py"):
            audit = scan_file(py_file)
            if audit:
                for sig in audit.signatures:
                    rg_signatures.add(sig.content_hash)
    
    logger.info(f"Indexed {len(rg_signatures)} unique logic blocks in apps_rg.")

    # 2. Audit Archives
    recovery_plan = []
    
    for root_path in ARCHIVE_ROOTS:
        root = Path(root_path)
        if not root.exists():
            logger.warning(f"Archive path not found: {root}")
            continue
            
        logger.info(f"Scanning Archive: {root.name}...")
        for py_file in root.rglob("*.py"):
            audit = scan_file(py_file)
            if not audit:
                continue

            # Check Redundancy
            matches = sum(1 for s in audit.signatures if s.content_hash in rg_signatures)
            total = len(audit.signatures)
            audit.redundancy_score = matches / total if total > 0 else 0.0
            
            # Logic for Recommendation
            if audit.redundancy_score == 1.0:
                audit.target_destination = "REJECT_DUPLICATE"
            elif audit.classification == "Engine":
                audit.target_destination = f"apps_rg/engines/{py_file.name}"
                audit.refactor_notes.append("Must inherit RGAgentBase")
            elif audit.classification == "Tool":
                audit.target_destination = f"apps_rg/shared/tools/{py_file.name}"
            elif audit.classification == "Type":
                new_name = py_file.stem.replace('Agent', '') + "_types.py"
                audit.target_destination = f"apps_rg/domain/types/{new_name}"
            
            recovery_plan.append(asdict(audit))

    # Output
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(recovery_plan, f, indent=2)
    
    logger.info(f"Audit Complete. Report saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
