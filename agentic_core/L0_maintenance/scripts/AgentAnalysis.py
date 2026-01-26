from pathlib import Path
from dataclasses import dataclass
from dataclasses import field

#!/usr/bin/env python3
"""
cache-First Hardening Report Generator

Identifies agents that need Redis/Pinecone cache-first logic hardening.
Meta-Learning is core to agentic DNA - every LLM call and key operation
MUST check Redis cache and Pinecone semantic memory FIRST.

Usage:
    python cache_first_hardening_report.py

Output:
    - List of agents missing cache-first patterns
    - Priority ranking based on LLM usage
    - Specific methods needing hardening
"""

import re


@dataclass
class AgentAnalysis:
    """Analysis result for a single agent file."""

    file_path: Path
    class_name: str
    has_redis_mixin: bool = False
    has_pinecone_mixin: bool = False
    has_llm_calls: bool = False
    has_cache_checks: bool = False
    has_semantic_lookup: bool = False
    methods_needing_hardening: list[str] = field(default_factory=list)
    priority: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

    def needs_hardening(self) -> bool:
        """Check if this agent needs cache-first hardening."""
        # If it has LLM calls but no cache checks, it needs hardening
        if self.has_llm_calls and not self.has_cache_checks:
            return True
        # If it has analysis methods but no semantic lookup
        if self.methods_needing_hardening and not self.has_semantic_lookup:
            return True
        return False


# Patterns indicating LLM usage
LLM_PATTERNS = [
    r"generate_content",
    r"gemini\.",
    r"llm\.",
    r"model\.generate",
    r"openai\.",
    r"anthropic\.",
    r"completion\(",
    r"chat\(",
]

# Patterns indicating cache-first logic
CACHE_PATTERNS = [
    r"cache_get",
    r"redis\.get",
    r"_local_cache",
    r"cached_result",
    r"from_cache",
]

# Patterns indicating semantic lookup
SEMANTIC_PATTERNS = [
    r"vector_search",
    r"pinecone.*query",
    r"semantic.*lookup",
    r"find_similar",
    r"embedding.*search",
]

# Methods that typically need cache-first hardening
METHODS_NEEDING_CACHE = [
    "analyze_violation",
    "analyze",
    "_analyze",
    "process_violation",
    "evaluate",
    "assess",
    "generate_fix",
    "suggest_resolution",
    "get_recommendation",
    "compute_embedding",
    "heal_repository",
]


def analyze_file(file_path: Path) -> AgentAnalysis | None:
    """Analyze a single agent file for cache-first patterns."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    # Extract class name
    class_match = re.search(r"class\s+(\w+Agent)\s*[:\(]", content)
    if not class_match:
        return None

    class_name = class_match.group(1)

    analysis = AgentAnalysis(
        file_path=file_path,
        class_name=class_name,
    )

    # Check for mixin inheritance
    analysis.has_redis_mixin = "RedisCacheMixin" in content
    analysis.has_pinecone_mixin = "PineconeVectorMixin" in content

    # Check for LLM calls
    for pattern in LLM_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            analysis.has_llm_calls = True
            break

    # Check for cache-first patterns
    for pattern in CACHE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            analysis.has_cache_checks = True
            break

    # Check for semantic lookup patterns
    for pattern in SEMANTIC_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            analysis.has_semantic_lookup = True
            break

    # Find methods needing hardening
    for method in METHODS_NEEDING_CACHE:
        if re.search(rf"def\s+{method}\s*\(", content):
            # Check if this method has cache logic
            method_match = re.search(
                rf"def\s+{method}\s*\([^)]*\)[^:]*:.*?(?=\n    def |\nclass |\Z)",
                content,
                re.DOTALL,
            )
            if method_match:
                method_body = method_match.group(0)
                has_cache = any(
                    re.search(p, method_body, re.IGNORECASE)
                    for p in CACHE_PATTERNS + SEMANTIC_PATTERNS
                )
                if not has_cache:
                    analysis.methods_needing_hardening.append(method)

    # Determine priority
    if analysis.has_llm_calls and not analysis.has_cache_checks:
        if "analyze" in str(analysis.methods_needing_hardening).lower():
            analysis.priority = "CRITICAL"
        else:
            analysis.priority = "HIGH"
    elif analysis.methods_needing_hardening:
        analysis.priority = "MEDIUM"
    else:
        analysis.priority = "LOW"

    return analysis


def scan_ssot_folders(project_root: Path) -> list[AgentAnalysis]:
    """Scan all SSOT folders for agents needing hardening."""
    ssot_folders = [
        project_root / "agentic_core" / "L0_maintenance",
        project_root / "agentic_core" / "L1_cognition",
        project_root / "agentic_core" / "L2_execution",
        project_root / "agentic_core" / "L3_orchestration",
        project_root / "agentic_core" / "L4_state",
        project_root / "agentic_core" / "L5_safety",
        project_root / "agentic_core" / "L6_observability",
    ]

    results = []

    for folder in ssot_folders:
        if not folder.exists():
            continue

        for agent_file in folder.rglob("*Agent.py"):
            # Skip backup folders
            if ".sovereign_healing_backup" in str(agent_file):
                continue
            if "__pycache__" in str(agent_file):
                continue

            analysis = analyze_file(agent_file)
            if analysis and analysis.needs_hardening():
                results.append(analysis)

    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    results.sort(key=lambda x: (priority_order.get(x.priority, 4), x.class_name))

    return results


def generate_report(results: list[AgentAnalysis]) -> str:
    """Generate a formatted report."""
    lines = [
        "=" * 80,
        "CACHE-FIRST HARDENING REPORT",
        "Meta-Learning DNA: Redis/Pinecone lookups MANDATORY before LLM calls",
        "=" * 80,
        "",
    ]

    # Group by priority
    by_priority = {}
    for r in results:
        by_priority.setdefault(r.priority, []).append(r)

    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        agents = by_priority.get(priority, [])
        if not agents:
            continue

        lines.append(f"\n{'=' * 40}")
        lines.append(f"PRIORITY: {priority} ({len(agents)} agents)")
        lines.append(f"{'=' * 40}")

        for agent in agents:
            lines.append(f"\n[FILE] {agent.file_path.relative_to(agent.file_path.parents[4])}")
            lines.append(f"   Class: {agent.class_name}")
            lines.append(f"   Has Redis Mixin: {'YES' if agent.has_redis_mixin else 'NO'}")
            lines.append(f"   Has Pinecone Mixin: {'YES' if agent.has_pinecone_mixin else 'NO'}")
            lines.append(f"   Has LLM Calls: {'YES' if agent.has_llm_calls else 'NO'}")
            lines.append(f"   Has cache Checks: {'YES' if agent.has_cache_checks else 'NO'}")
            lines.append(f"   Has Semantic Lookup: {'YES' if agent.has_semantic_lookup else 'NO'}")

            if agent.methods_needing_hardening:
                lines.append("   Methods needing hardening:")
                for method in agent.methods_needing_hardening:
                    lines.append(f"      - {method}()")

    # Summary
    lines.append("\n" + "=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Total agents needing hardening: {len(results)}")
    lines.append(f"  CRITICAL: {len(by_priority.get('CRITICAL', []))}")
    lines.append(f"  HIGH: {len(by_priority.get('HIGH', []))}")
    lines.append(f"  MEDIUM: {len(by_priority.get('MEDIUM', []))}")
    lines.append(f"  LOW: {len(by_priority.get('LOW', []))}")

    # Hardening checklist
    lines.append("\n" + "=" * 80)
    lines.append("HARDENING CHECKLIST")
    lines.append("=" * 80)
    lines.append("""
For each agent, implement the cache-first pattern:

1. BEFORE any LLM call:
   ```python
   # Step 1: Check Redis cache
   cache_key = f"{self._cache_prefix}:{operation}:{hash(input)}"
   cached = await self.cache_get(cache_key)
   if cached:
       return cached

   # Step 2: Check Pinecone semantic memory
   embedding = await self._get_embedding(input)
   similar = await self.vector_search(embedding, top_k=3)
   if similar and similar[0]['score'] > 0.95:
       return similar[0]['metadata']['result']

   # Step 3: Only NOW call LLM
   result = await self._llm_generate(prompt)

   # Step 4: Store in both caches
   await self.cache_set(cache_key, result, ttl=3600)
   await self.vector_upsert(embedding, metadata={'result': result})

   return result
   ```

2. For analyze_violation methods:
   - Hash the violation signature
   - Check if similar violation was seen before
   - Reuse previous fix if confidence > 0.9

3. For heal_repository methods:
   - cache scan results with file hashes
   - Invalidate on file changes
   - Store successful fixes in Pinecone for pattern learning
""")

    return "\n".join(lines)


if __name__ == "__main__":
    project_root = Path(__file__).parents[3]
    results = scan_ssot_folders(project_root)
    report = generate_report(results)
    # [HYGIENE] Removed debug print: print(report)

    # Also save to file
    report_path = (
        project_root / "agentic_core" / "L0_maintenance" / "reports" / "cache_first_hardening.txt"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    # [HYGIENE] Removed debug print: print(f"\nReport saved to: {report_path}")
