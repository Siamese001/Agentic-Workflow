import copy
from typing import List, Dict, Any
from utils_types import BudgetConfig


def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Deterministic shallow normalization
    normed = []
    for r in results:
        normed.append({
            "query": r.get("query", ""),
            "rank": r.get("rank", 0),
            "evidence": r.get("evidence", ""),
        })
    return normed


def dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for r in results:
        key = (r.get("query", ""), r.get("evidence", ""))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def truncate_by_budget(results: List[Dict[str, Any]], config: BudgetConfig) -> List[Dict[str, Any]]:
    # Trim to max_rag_items
    if len(results) <= config.max_rag_items:
        return results
    return results[-config.max_rag_items:]
