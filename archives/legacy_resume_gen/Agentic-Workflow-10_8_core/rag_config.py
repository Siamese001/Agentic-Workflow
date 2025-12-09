from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RetrievalConfig:
    queries: List[str]
    filters: Dict[str, object]
    ranking: Dict[str, object]
    metadata: Dict[str, object] | None = None

    def to_plan_fragment(self) -> Dict[str, object]:
        return {
            "queries": self.queries,
            "filters": self.filters,
            "ranking": self.ranking,
            "metadata": self.metadata or {},
        }
