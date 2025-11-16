from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RetrievalConfig:
    queries: List[str]
    filters: Dict[str, Any]
    ranking: Dict[str, Any]

    def to_plan_fragment(self) -> Dict[str, Any]:
        return {
            "queries": self.queries,
            "filters": self.filters,
            "ranking": self.ranking,
        }
