from __future__ import annotations

"""
⚛️ Deep Brain Harvest - Pinecone Pattern Storage

This script extracts the Subatomic Flattening Pattern and stores it in Pinecone
for global retrieval and application across the codebase.

Usage:
    python scripts/deep_brain_harvest.py --pattern flattening --namespace structural_patterns
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from pinecone import Pinecone, ServerlessSpec

    PINECONE_AVAILABLE: Any = True
except ImportError:
    PINECONE_AVAILABLE: Any = False
    print("⚠️  Pinecone not available. Install with: pip install pinecone-client")
from agentic_core.patterns.subatomic_flattening_rule import get_flattening_pattern

logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)


class DeepBrainHarvester:
    """Harvests and stores patterns in Pinecone Deep Brain."""

    def __init__(self, api_key: str = None, index_name: str = "canon-healing-patterns"):
        """
        Initialize Deep Brain Harvester.

        Args:
            api_key: Pinecone API key (defaults to env var)
            index_name: Pinecone index name
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone client not available")
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment")
        self.index_name = index_name
        self.pc = Pinecone(api_key=self.api_key)
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)
        Logger.info(f"✅ Connected to Pinecone index: {self.index_name}")

    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if not."""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            Logger.info(f"Creating new index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,
                Metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            Logger.info(f"✅ Created index: {self.index_name}")
        else:
            Logger.info(f"✅ Index already exists: {self.index_name}")

    def _generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            import openai

            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.embeddings.create(model="text-embedding-ada-002", input=text)
            return response.data[0].embedding
        except Exception as e:
            Logger.error(f"Error generating embedding: {e}")
            return [0.0] * 1536

    def harvest_flattening_pattern(self, namespace: str = "structural_patterns") -> dict:
        """
        Harvest the Subatomic Flattening Pattern and store in Pinecone.

        Args:
            namespace: Pinecone namespace for pattern storage

        Returns:
            Upsert result
        """
        Logger.info("🌾 Harvesting Subatomic Flattening Pattern...")
        pattern: Any = get_flattening_pattern()
        pattern_text: Any = self._create_pattern_text(pattern)
        Logger.info("🧠 Generating embedding...")
        embedding: Any = self._generate_embedding(pattern_text)
        metadata: Any = {
            "pattern_type": "subatomic_flattening",
            "source_file": pattern["source_file"],
            "method_name": pattern["method_name"],
            "date": pattern["date"],
            "before_lines": pattern["before"]["lines"],
            "after_lines": pattern["after"]["lines"],
            "nesting_reduction": pattern["after"]["improvements"][1],
            "preservation_rate": pattern["success_metrics"]["preservation_rate"],
            "trigger": pattern["reusable_pattern"]["trigger"],
            "pattern_text": pattern_text[:1000],
        }
        Logger.info(f"📤 Upserting to Pinecone namespace: {namespace}")
        result: Any = self.index.upsert(
            vectors=[
                {
                    "id": "flattening_pattern_agent_logic_2025_12_19",
                    "values": embedding,
                    "metadata": metadata,
                }
            ],
            namespace=namespace,
        )
        Logger.info(f"✅ Pattern harvested successfully: {result}")
        return result

    def _create_pattern_text(self, pattern: dict) -> str:
        """
        Create searchable text representation of pattern.

        Args:
            pattern: Pattern dictionary

        Returns:
            Text representation for embedding
        """
        text_parts = [
            "# Subatomic Flattening Pattern",
            "",
            f"## Trigger: {pattern['reusable_pattern']['trigger']}",
            "",
            "## Problem:",
            f"Method with {pattern['before']['lines']} lines and {pattern['before']['nesting_depth']} nesting levels",
            "Issues: " + ", ".join(pattern["before"]["issues"]),
            "",
            "## Solution:",
            "Extract nested logic into focused helper methods",
            "",
            "## Recognition Patterns:",
            *[f"- {p}" for p in pattern["reusable_pattern"]["recognition"]],
            "",
            "## Extraction Heuristic:",
            *[
                f"{i}. {step}"
                for i, step in enumerate(pattern["reusable_pattern"]["extraction_heuristic"], 1)
            ],
            "",
            "## Naming Convention:",
            *[f"- {k}: {v}" for k, v in pattern["reusable_pattern"]["naming_convention"].items()],
            "",
            "## Results:",
            f"- Line reduction: {pattern['success_metrics']['complexity_reduction']}%",
            f"- Nesting reduction: {pattern['success_metrics']['nesting_reduction']}%",
            f"- Preservation: {pattern['success_metrics']['preservation_rate']}%",
            f"- Healing readiness: {pattern['success_metrics']['healing_readiness']}",
            "",
            "## Example:",
            f"Source: {pattern['source_file']}",
            f"Method: {pattern['method_name']}",
            f"Before: {pattern['before']['lines']} lines, {pattern['before']['nesting_depth']} levels",
            f"After: {pattern['after']['lines']} lines, {pattern['after']['nesting_depth']} levels",
            "",
            "## Extracted Helpers:",
            *[
                f"- {helper['name']}: {helper['purpose']} ({helper['lines']} lines, {helper['nesting']} nesting)"
                for helper in pattern["helper_methods"]
            ],
        ]
        return "\n".join(text_parts)

    def query_pattern(
        self, query: str, namespace: str = "structural_patterns", top_k: int = 3
    ) -> list[dict]:
        """
        Query Pinecone for similar patterns.

        Args:
            query: Query text
            namespace: Namespace to search
            top_k: Number of results to return

        Returns:
            List of matching patterns
        """
        Logger.info(f"🔍 Querying pattern: {query}")
        query_embedding: Any = self._generate_embedding(query)
        results: Any = self.index.query(
            vector=query_embedding, top_k=top_k, namespace=namespace, include_metadata=True
        )
        Logger.info(f"✅ Found {len(results.matches)} matches")
        return [
            {"id": match.id, "score": match.score, "metadata": match.metadata}
            for match in results.matches
        ]


def main() -> Any:
    """Main entry point for Deep Brain Harvest."""
    parser: Any = argparse.ArgumentParser(description="Harvest patterns into Pinecone Deep Brain")
    parser.add_argument(
        "--pattern", choices=["flattening"], default="flattening", help="Pattern to harvest"
    )
    parser.add_argument("--namespace", default="structural_patterns", help="Pinecone namespace")
    parser.add_argument("--index", default="canon-healing-patterns", help="Pinecone index name")
    parser.add_argument("--query", help="Query for existing patterns instead of upserting")
    args: Any = parser.parse_args()
    try:
        harvester: Any = DeepBrainHarvester(index_name=args.index)
        if args.query:
            results: Any = harvester.query_pattern(args.query, namespace=args.namespace)
            print("\n🔍 Query Results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['id']} (score: {result['score']:.4f})")
                print(f"   Trigger: {result['metadata'].get('trigger', 'N/A')}")
                print(f"   Reduction: {result['metadata'].get('nesting_reduction', 'N/A')}")
        elif args.pattern == "flattening":
            result: Any = harvester.harvest_flattening_pattern(namespace=args.namespace)
            print("\n✅ Flattening pattern harvested successfully!")
            print(f"   Namespace: {args.namespace}")
            print(f"   Index: {args.index}")
            print(f"   Upserted: {result.upserted_count} vectors")
    except Exception as e:
        Logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
