"""
ExperienceBuffer – Persistent learning from outcomes
"""
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime


class ExperienceBuffer:
    def __init__(self, path: Path, max_entries: int = 1000):
        self.path = path
        self.max_entries = max_entries
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def record(self, entry: Dict[str, Any]):
        entries = self.load()
        entry["timestamp"] = datetime.utcnow().isoformat()
        entries.append(entry)
        if len(entries) > self.max_entries:
            entries = entries[-self.max_entries:]
        self.path.write_text(json.dumps(entries, indent=2))

    def load(self) -> List[Dict]:
        try:
            return json.loads(self.path.read_text())
        except:
            return []

    def find_similar(self, **filters) -> List[Dict]:
        entries = self.load()
        results = []
        for e in entries:
            if all(e.get(k) == v for k, v in filters.items()):
                results.append(e)
        return results[-50:]  # Most recent
