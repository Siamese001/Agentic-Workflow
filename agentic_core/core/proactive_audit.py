"""
Proactive Fission Scanner - L3 Orchestration

Scans L4 State for structural patterns matching known 'Critical Bloat' profiles.
Identifies files likely to cause Key 41/42 violations before they fail.

Strategy:
- Scan repository for high-gravity files (>600 lines)
- Use Brave Search for modular design patterns
- Use Pinecone to find structural twins
- Create pre-emptive refactor proposals
- Enable proactive architectural governance
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ProactiveFissionScanner:
    """
    L3 Orchestrator: Scans the L4 State for structural patterns
    matching known 'Critical Bloat' profiles.
    
    Process:
    1. Scan repository for files exceeding line threshold
    2. Query Brave Search for modular design patterns
    3. Use Pinecone to find structural twins
    4. Generate pre-emptive fission strategies
    5. Create GitKraken refactor proposal branches
    """
    
    def __init__(self, mcp_router, line_threshold: int = 600):
        """
        Initialize Proactive Fission Scanner.
        
        Args:
            mcp_router: MCPRouter instance for MCP calls
            line_threshold: Line count threshold for bloat detection
        """
        self.router = mcp_router
        self.threshold = line_threshold
        logger.info(f"✅ Proactive Scanner initialized (threshold: {line_threshold} lines)")
    
    def get_line_count(self, file_path: str) -> int:
        """
        Get line count for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Number of lines in file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except Exception as e:
            logger.warning(f"   ⚠️  Could not read {file_path}: {e}")
            return 0
    
    async def scan_repository(self, target_dir: str) -> List[Dict[str, any]]:
        """
        Identifies files that meet the 'Atomic Criticality' criteria.
        
        Args:
            target_dir: Directory to scan
            
        Returns:
            List of candidate files with metadata
        """
        logger.info(f"🔍 Scanning repository: {target_dir}")
        candidates = []
        
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    line_count = self.get_line_count(path)
                    
                    if line_count > self.threshold:
                        candidates.append({
                            "path": path,
                            "line_count": line_count,
                            "severity": self._calculate_severity(line_count),
                            "relative_path": os.path.relpath(path, target_dir)
                        })
                        logger.info(f"   🚨 Bloat detected: {file} ({line_count} lines)")
        
        logger.info(f"   ✅ Scan complete: {len(candidates)} candidates found")
        return candidates
    
    def _calculate_severity(self, line_count: int) -> str:
        """
        Calculate severity level based on line count.
        
        Args:
            line_count: Number of lines
            
        Returns:
            Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if line_count < 700:
            return "LOW"
        elif line_count < 850:
            return "MEDIUM"
        elif line_count < 1000:
            return "HIGH"
        else:
            return "CRITICAL"
    
    async def generate_pre_emptive_strategy(self, file_path: str) -> Dict[str, any]:
        """
        Uses Brave Search to find the best modular split for the specific file type.
        
        Args:
            file_path: Path to file
            
        Returns:
            Strategy dictionary with design patterns
        """
        file_name = os.path.basename(file_path)
        logger.info(f"🧠 Generating strategy for {file_name}")
        
        try:
            # Query Brave Search for modular design patterns
            query = f"best modular architecture for python {file_name}"
            design_patterns = await self.router.call_mcp("brave_search", {
                "query": query,
                "purpose": "Find modular design patterns"
            })
            
            # Query Pinecone for structural twins
            structural_twins = await self.router.call_mcp("pinecone", {
                "query": f"similar structure to {file_name}",
                "top_k": 3,
                "purpose": "Find files with similar structure"
            })
            
            strategy = {
                "file_path": file_path,
                "design_patterns": design_patterns,
                "structural_twins": structural_twins,
                "recommended_split": self._recommend_split(file_path)
            }
            
            logger.info(f"   ✅ Strategy generated")
            return strategy
        
        except Exception as e:
            logger.error(f"   ❌ Strategy generation failed: {e}")
            return {"file_path": file_path, "error": str(e)}
    
    def _recommend_split(self, file_path: str) -> Dict[str, str]:
        """
        Recommend split pattern based on file name and content.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary of recommended file splits
        """
        base_name = Path(file_path).stem
        parent_dir = Path(file_path).parent
        
        return {
            "core": f"{parent_dir}/{base_name}_core.py",
            "signals": f"{parent_dir}/{base_name}_signals.py",
            "utils": f"{parent_dir}/{base_name}_utils.py",
            "facade": file_path
        }
    
    async def create_refactor_proposal(self, candidates: List[Dict[str, any]]) -> str:
        """
        Creates a GitKraken refactor proposal branch.
        
        Args:
            candidates: List of bloat candidates
            
        Returns:
            Branch name created
        """
        if not candidates:
            logger.info("   ℹ️  No candidates for refactor proposal")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"proactive-refactor-{timestamp}"
        
        logger.info(f"🌿 Creating refactor proposal branch: {branch_name}")
        
        try:
            await self.router.call_mcp("gitkraken", {
                "action": "create_branch",
                "name": branch_name
            })
            
            # Store proposal in Redis
            await self.router.call_mcp("redis", {
                "action": "set",
                "key": f"refactor_proposal:{branch_name}",
                "value": str(len(candidates))
            })
            
            logger.info(f"   ✅ Refactor proposal created: {len(candidates)} files")
            return branch_name
        
        except Exception as e:
            logger.error(f"   ❌ Failed to create refactor proposal: {e}")
            return None
    
    async def generate_audit_report(self, candidates: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Generate comprehensive audit report.
        
        Args:
            candidates: List of bloat candidates
            
        Returns:
            Audit report dictionary
        """
        logger.info(f"📊 Generating audit report")
        
        severity_counts = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }
        
        total_lines = 0
        
        for candidate in candidates:
            severity_counts[candidate["severity"]] += 1
            total_lines += candidate["line_count"]
        
        report = {
            "total_candidates": len(candidates),
            "severity_breakdown": severity_counts,
            "total_lines": total_lines,
            "average_lines": total_lines // len(candidates) if candidates else 0,
            "candidates": candidates
        }
        
        logger.info(f"   ✅ Report generated: {len(candidates)} candidates")
        logger.info(f"      CRITICAL: {severity_counts['CRITICAL']}")
        logger.info(f"      HIGH: {severity_counts['HIGH']}")
        logger.info(f"      MEDIUM: {severity_counts['MEDIUM']}")
        logger.info(f"      LOW: {severity_counts['LOW']}")
        
        return report


def get_proactive_scanner(mcp_router, line_threshold: int = 600) -> ProactiveFissionScanner:
    """
    Factory function to create ProactiveFissionScanner instance.
    
    Args:
        mcp_router: MCPRouter instance
        line_threshold: Line count threshold
        
    Returns:
        ProactiveFissionScanner instance
    """
    return ProactiveFissionScanner(mcp_router=mcp_router, line_threshold=line_threshold)


# Integration Example for orchestrator_main.py:
"""
from agentic_core.core.proactive_audit import ProactiveFissionScanner
from agentic_core.infra.mcp_router import MCPRouter
from agentic_core.infra.tui_dashboard import AgenticTUI

# Initialize components
mcp_router = MCPRouter(tui_handle=tui)
scanner = ProactiveFissionScanner(mcp_router=mcp_router, line_threshold=600)

# Run proactive scan
candidates = await scanner.scan_repository("agentic_core/")

# Generate strategies for each candidate
for candidate in candidates:
    strategy = await scanner.generate_pre_emptive_strategy(candidate["path"])
    print(f"Strategy for {candidate['path']}: {strategy}")

# Create refactor proposal branch
branch_name = await scanner.create_refactor_proposal(candidates)

# Generate audit report
report = await scanner.generate_audit_report(candidates)
print(f"Audit Report: {report}")
"""
