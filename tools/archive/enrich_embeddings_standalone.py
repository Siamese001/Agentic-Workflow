#!/usr/bin/env python3
"""
ARCHIVED: Semantic Enrichment and Embedding Optimization Pipeline

This script has been archived because:
1. It has been migrated to use the canonical SemanticEnricher from agentic_core
2. The script writes to 'agentic_best_practices_semantic' collection which is not read by production code
3. New code should use agentic_core.knowledge.enrichment.semantic_enricher.SemanticEnricher directly

Archived: 2026-04-06
Reason: GAP-4 remediation - orphaned semantic collection writes
Reference: .windsurf/plans/fact-vec-gap-remediation-bf6908.md

Original description:
Transforms raw ChromaDB chunks into higher-quality semantic units
optimized for agentic AI retrieval.

Input: agentic_best_practices collection (raw chunks)
Output: agentic_best_practices_semantic collection (enriched semantic units)
"""

import argparse
import hashlib
import re
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Use canonical SemanticEnricher from agentic_core
from agentic_core.knowledge.enrichment.semantic_enricher import SemanticEnricher


class _LegacyRuleBasedEnricher:
    """DEPRECATED: Rule-based semantic enrichment for agentic AI content.

    This is the legacy implementation. New code should use:
    agentic_core.knowledge.enrichment.semantic_enricher.SemanticEnricher

    Kept for reference only; this entire script is archived.
    """

    # Agentic AI pattern keywords
    AGENTIC_PATTERNS = {
        "retrieval": ["retrieval", "rag", "fetch", "query", "search", "index"],
        "orchestration": ["orchestrat", "workflow", "pipeline", "coordination", "agent"],
        "evaluation": ["evaluat", "metric", "benchmark", "assessment", "performance"],
        "memory": ["memory", "storage", "cache", "persistence", "database"],
        "safety_governance": ["safety", "governance", "guardrail", "policy", "compliance"]
    }

    # Core concept indicators
    CONCEPT_INDICATORS = [
        "embedding", "vector", "semantic", "chunk", "document", "knowledge",
        "reasoning", "inference", "generation", "prompt", "context", "grounding"
    ]

    # Query expansion synonyms
    QUERY_SYNONYMS = {
        "retrieval": ["fetch", "search", "query", "lookup", "find"],
        "embedding": ["vector", "representation", "encoding"],
        "agent": ["assistant", "ai", "model", "system"],
        "orchestration": ["coordination", "workflow", "pipeline"],
        "evaluation": ["assessment", "benchmark", "metric", "performance"]
    }

    def __init__(self):
        self.concept_patterns = self._build_concept_patterns()

    def _build_concept_patterns(self) -> set[str]:
        """Build regex patterns for concept extraction."""
        patterns = set()
        for concept in self.CONCEPT_INDICATORS:
            patterns.add(rf'\b{concept}\w*\b')
        return patterns

    def _extract_title(self, text: str) -> str:
        """Extract best-guess title from text."""
        lines = text.strip().split('\n')

        # Look for markdown headers
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line.startswith('#'):
                return line.lstrip('#').strip()

        # Look for all-caps or title-case lines
        for line in lines[:3]:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                if line.isupper() or line.istitle():
                    return line

        # Fallback: first sentence (truncated)
        first_sentence = text.split('.')[0].strip()
        if len(first_sentence) > 50:
            return first_sentence[:47] + "..."
        return first_sentence or "Untitled"

    def _extract_key_concepts(self, text: str) -> list[str]:
        """Extract key concepts using simple NLP heuristics."""
        concepts = []
        text_lower = text.lower()

        # Find concept indicators
        for concept in self.CONCEPT_INDICATORS:
            if concept in text_lower:
                concepts.append(concept.capitalize())

        # Extract noun phrases (simple heuristic)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for word in words:
            if len(word) > 3 and word not in concepts:
                concepts.append(word)

        # Limit to top concepts
        return list(dict.fromkeys(concepts))[:8]  # Remove duplicates, limit to 8

    def _detect_agentic_patterns(self, text: str) -> list[str]:
        """Detect agentic AI patterns in text."""
        patterns = []
        text_lower = text.lower()

        for pattern_name, keywords in self.AGENTIC_PATTERNS.items():
            if any(keyword in text_lower for keyword in keywords):
                patterns.append(pattern_name.replace("_", " ").title())

        return patterns

    def _extract_execution_insight(self, text: str) -> str:
        """Extract execution-relevant insight."""
        text_lower = text.lower()

        # Look for implementation clues
        implementation_keywords = ["implement", "build", "create", "use", "apply", "integrate"]
        if any(keyword in text_lower for keyword in implementation_keywords):
            # Find sentence with implementation clue
            sentences = text.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in implementation_keywords):
                    return sentence.strip()[:200] + "..." if len(sentence.strip()) > 200 else sentence.strip()

        # Fallback: what this enables
        if "enable" in text_lower or "allow" in text_lower:
            sentences = text.split('.')
            for sentence in sentences:
                if "enable" in sentence.lower() or "allow" in sentence.lower():
                    return sentence.strip()[:200] + "..." if len(sentence.strip()) > 200 else sentence.strip()

        return "Implementation guidance for agentic systems"

    def _generate_query_expansion(self, text: str) -> list[str]:
        """Generate query expansion terms."""
        expansion_terms = []
        text_lower = text.lower()

        for concept, synonyms in self.QUERY_SYNONYMS.items():
            if concept in text_lower:
                expansion_terms.extend(synonyms)

        # Add key concepts as expansion terms
        concepts = self._extract_key_concepts(text)
        for concept in concepts:
            if concept.lower() not in text_lower:
                expansion_terms.append(concept.lower())

        return list(dict.fromkeys(expansion_terms))[:10]  # Remove duplicates, limit to 10

    def enrich_chunk(self, chunk_text: str, metadata: dict) -> dict:
        """Transform raw chunk into structured semantic representation."""
        # Clean text
        cleaned_text = re.sub(r'\s+', ' ', chunk_text.strip())

        # Extract components
        title = self._extract_title(cleaned_text)
        key_concepts = self._extract_key_concepts(cleaned_text)
        agentic_patterns = self._detect_agentic_patterns(cleaned_text)
        execution_insight = self._extract_execution_insight(cleaned_text)
        query_expansion = self._generate_query_expansion(cleaned_text)

        # Build summary (first 2-4 sentences)
        sentences = [s.strip() for s in cleaned_text.split('.') if s.strip()]
        summary = '. '.join(sentences[:3]) + '.' if len(sentences) >= 3 else cleaned_text[:200] + "..."

        # Build enriched representation
        enriched_parts = [
            f"Title: {title}",
            f"Summary: {summary}",
            f"Key Concepts: {', '.join(key_concepts)}" if key_concepts else "",
            f"Agentic Patterns: {', '.join(agentic_patterns)}" if agentic_patterns else "",
            f"Execution Insight: {execution_insight}",
            f"Query Expansion: {', '.join(query_expansion)}" if query_expansion else "",
            f"Source Context: {metadata.get('source_url', 'Unknown source')}"
        ]

        enriched_text = '\n\n'.join(filter(None, enriched_parts))

        # Generate enrichment hash
        enrichment_hash = hashlib.sha256(enriched_text.encode()).hexdigest()

        return {
            'enriched_text': enriched_text,
            'title': title,
            'summary': summary,
            'key_concepts': key_concepts,
            'agentic_patterns': agentic_patterns,
            'execution_insight': execution_insight,
            'query_expansion': query_expansion,
            'enrichment_hash': enrichment_hash
        }


class SemanticPipeline:
    """Main pipeline for semantic enrichment and embedding optimization."""

    def __init__(self, chroma_path: str, rebuild: bool = False):
        self.chroma_path = Path(chroma_path)
        self.rebuild = rebuild
        self.enricher = SemanticEnricher()  # Canonical from agentic_core

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.chroma_path), settings=Settings(allow_reset=True))

        # Collections
        self.source_collection = self.client.get_or_create_collection("agentic_best_practices")
        self.target_collection = self.client.get_or_create_collection("agentic_best_practices_semantic")

        # Initialize embedding model
        self.model = SentenceTransformer('BAAI/bge-m3')

        # Statistics
        self.stats = {
            'processed': 0,
            'enriched': 0,
            'skipped': 0,
            'stored': 0,
            'errors': 0
        }

    def _reset_target_collection(self):
        """Reset target collection if rebuild flag is set."""
        if self.rebuild:
            self.client.delete_collection("agentic_best_practices_semantic")
            self.target_collection = self.client.get_or_create_collection("agentic_best_practices_semantic")
            print("Target collection reset.")

    def _check_existing_hash(self, enrichment_hash: str) -> bool:
        """Check if enrichment hash already exists in target collection."""
        try:
            result = self.target_collection.get(
                where={"enrichment_hash": enrichment_hash},
                limit=1
            )
            return len(result['ids']) > 0
        except Exception:
            return False

    def _batch_embed(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Batch embed texts using BGE-M3."""
        embeddings = []

        for i in tqdm(range(0, len(texts), batch_size), desc="Embedding batches"):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, normalize_embeddings=True)
            embeddings.extend(batch_embeddings.tolist())

        return embeddings

    def _process_chunk(self, chunk_id: str, chunk_text: str, metadata: dict) -> dict | None:
        """Process a single chunk through enrichment pipeline."""
        try:
            # Enrich chunk using canonical SemanticEnricher adapter
            enriched = self.enricher.enrich_chunk_adapter(chunk_text, metadata)

            # Check for duplicates
            if self._check_existing_hash(enriched['enrichment_hash']):
                self.stats['skipped'] += 1
                return None

            # Prepare enriched metadata (ensure list values are never empty)
            enriched_metadata = metadata.copy()
            enriched_metadata.update({
                'semantic_version': 'v1',
                'enrichment_type': 'agentic_semantic',
                'original_chunk_id': chunk_id,
                'enrichment_hash': enriched['enrichment_hash'],
                'title': enriched['title'],
                'key_concepts': enriched['key_concepts'] or ['general'],
                'agentic_patterns': enriched['agentic_patterns'] or ['general']
            })

            self.stats['enriched'] += 1
            return {
                'id': f"semantic_{chunk_id}",
                'text': enriched['enriched_text'],
                'metadata': enriched_metadata
            }

        except Exception as e:
            print(f"Error processing chunk {chunk_id}: {e}")
            self.stats['errors'] += 1
            return None

    def run(self, limit: int | None = None, sample_size: int = 0):
        """Run the semantic enrichment pipeline."""
        print("Starting semantic enrichment pipeline...")
        print(f"Source collection: {self.source_collection.name}")
        print(f"Target collection: {self.target_collection.name}")
        print(f"Rebuild: {self.rebuild}")

        # Reset target collection if requested
        self._reset_target_collection()

        # Get source chunks
        if limit:
            result = self.source_collection.get(limit=limit)
        else:
            result = self.source_collection.get()

        chunk_ids = result['ids']
        chunk_texts = result['documents']
        chunk_metadatas = result['metadatas']

        total_chunks = len(chunk_ids)
        print(f"Found {total_chunks} chunks to process")

        if sample_size and sample_size > 0:
            chunk_ids = chunk_ids[:sample_size]
            chunk_texts = chunk_texts[:sample_size]
            chunk_metadatas = chunk_metadatas[:sample_size]
            print(f"Processing sample of {len(chunk_ids)} chunks")

        # Process chunks
        processed_chunks = []

        for chunk_id, chunk_text, metadata in tqdm(
            zip(chunk_ids, chunk_texts, chunk_metadatas),
            total=len(chunk_ids),
            desc="Processing chunks"
        ):
            self.stats['processed'] += 1

            processed_chunk = self._process_chunk(chunk_id, chunk_text, metadata or {})
            if processed_chunk:
                processed_chunks.append(processed_chunk)

        print(f"Processed: {self.stats['processed']}")
        print(f"Enriched: {self.stats['enriched']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")

        if not processed_chunks:
            print("No chunks to store.")
            return

        # Batch embed enriched texts
        enriched_texts = [chunk['text'] for chunk in processed_chunks]
        print(f"Embedding {len(enriched_texts)} enriched chunks...")

        embeddings = self._batch_embed(enriched_texts)

        # Store in target collection
        ids = [chunk['id'] for chunk in processed_chunks]
        metadatas = [chunk['metadata'] for chunk in processed_chunks]

        print(f"Storing {len(ids)} semantic chunks...")

        self.target_collection.add(
            ids=ids,
            documents=enriched_texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        self.stats['stored'] = len(ids)

        print(f"Stored: {self.stats['stored']}")
        print("Pipeline completed successfully!")

        # Print sample enriched chunk
        if processed_chunks:
            print("\n--- Sample Enriched Chunk ---")
            print(processed_chunks[0]['text'])
            print("-------------------------------")

    def query_semantic(self, query: str, n_results: int = 5) -> list[dict]:
        """Query the semantic collection with expansion."""
        # Expand query
        expanded_terms = []
        query_lower = query.lower()

        for concept, synonyms in self.enricher.QUERY_SYNONYMS.items():
            if concept in query_lower:
                expanded_terms.extend(synonyms)

        # Build expanded query
        expanded_query = query
        if expanded_terms:
            expanded_query += " " + " ".join(expanded_terms)

        # Embed query
        query_embedding = self.model.encode([expanded_query], normalize_embeddings=True)

        # Search
        results = self.target_collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return formatted_results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Semantic Enrichment Pipeline")
    parser.add_argument("--chroma-path", default="artifacts/chromadb",
                       help="Path to ChromaDB directory")
    parser.add_argument("--rebuild", action="store_true",
                       help="Rebuild target collection")
    parser.add_argument("--limit", type=int,
                       help="Limit number of chunks to process")
    parser.add_argument("--sample", type=int,
                       help="Process sample of N chunks")
    parser.add_argument("--query", type=str,
                       help="Test query against semantic collection")

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = SemanticPipeline(args.chroma_path, args.rebuild)

    if args.query:
        # Test query
        results = pipeline.query_semantic(args.query)
        print(f"\nQuery results for: '{args.query}'")
        print("=" * 50)
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (Distance: {result.get('distance', 'N/A'):.4f}):")
            print(f"Title: {result['metadata'].get('title', 'N/A')}")
            print(f"Patterns: {result['metadata'].get('agentic_patterns', [])}")
            print(f"Content: {result['document'][:300]}...")
    else:
        # Run pipeline
        pipeline.run(limit=args.limit, sample_size=args.sample)

        # Print final statistics
        print("\n--- Final Statistics ---")
        print(f"Processed: {pipeline.stats['processed']}")
        print(f"Enriched: {pipeline.stats['enriched']}")
        print(f"Skipped: {pipeline.stats['skipped']}")
        print(f"Stored: {pipeline.stats['stored']}")
        print(f"Errors: {pipeline.stats['errors']}")


if __name__ == "__main__":
    main()