#!/usr/bin/env python3
"""
Query Canon - Semantic Search Interface

Allows querying the Canon for relevant code patterns and knowledge.
Uses the same hardened infrastructure as the ETL pipeline.
"""

import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime

# Import our hardened infrastructure
from connection_manager import ConnectionManager
from schemas_connectivity import CanonEntry, CanonMetadata
from agent_logic_connectivity import CanonValidator

class CanonQuery:
    def __init__(self, similarity_threshold: float = 0.70):
        """Initialize the query interface."""
        self.cm = ConnectionManager()
        self.validator = CanonValidator(similarity_threshold=similarity_threshold)
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()
        self.embedding_fn = self.cm.get_embedding

    def query(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the Canon for relevant information.
        
        Args:
            question: Natural language query or code snippet
            top_k: Number of results to return
            
        Returns:
            List of relevant matches with metadata
        """
        print(f"\n🔍 Querying Canon: '{question}'")
        print("=" * 60)
        
        # Generate embedding for the query
        try:
            query_embedding = self.embedding_fn(question)
            print(f"✅ Generated query embedding ({len(query_embedding)} dimensions)")
        except Exception as e:
            print(f"❌ Failed to generate embedding: {e}")
            return []
        
        # Query Pinecone (L2) for semantic matches
        results = []
        try:
            pinecone_results = self.pinecone_index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            if pinecone_results and pinecone_results.get('matches'):
                for match in pinecone_results['matches']:
                    metadata = match.get('metadata', {})
                    results.append({
                        'id': match['id'],
                        'score': match['score'],
                        'content': metadata.get('content', 'Content not available'),
                        'project_context': metadata.get('project_context', 'Unknown'),
                        'canon_rule_id': metadata.get('canon_rule_id', 'Unknown'),
                        'failure_count': metadata.get('failure_count', 0),
                        'success_count': metadata.get('success_count', 0),
                        'source': 'pinecone'
                    })
                    
        except Exception as e:
            print(f"❌ Pinecone query failed: {e}")
        
        # Sort by similarity score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

    def format_results(self, results: List[Dict[str, Any]], query: str) -> None:
        """Display query results in a readable format."""
        if not results:
            print("\n❌ No matches found in Canon.")
            return
        
        print(f"\n📊 Found {len(results)} relevant results:")
        print("=" * 60)
        
        for i, result in enumerate(results[:5], 1):  # Show top 5
            print(f"\n{i}. Match Score: {result['score']:.4f}")
            print(f"   📁 Context: {result['project_context']}")
            print(f"   🏷️  Rule ID: {result['canon_rule_id']}")
            print(f"   📈 Stats: {result['success_count']} success, {result['failure_count']} failures")
            print(f"\n   📄 Content:")
            # Truncate very long content for display
            content = result['content']
            if len(content) > 500:
                content = content[:500] + "...\n[truncated]"
            print("   " + "\n   ".join(content.split('\n')))
            print("-" * 60)
        
        # Suggest follow-up actions
        best_match = results[0]
        if best_match['score'] > 0.9:
            print(f"\n✅ Excellent match found! (Score: {best_match['score']:.4f})")
        elif best_match['score'] > 0.75:
            print(f"\n✅ Good match found. (Score: {best_match['score']:.4f})")
        else:
            print(f"\n⚠️  Matches are below optimal threshold. Consider rephrasing your query.")

def main():
    parser = argparse.ArgumentParser(
        description="Query the Canon for relevant code patterns and knowledge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query_canon.py "How do I separate cognitive and action planes?"
  python query_canon.py "def validate_cognitive_action_separation" --top 3
  python query_canon.py "error handling in async functions" --threshold 0.6
        """
    )
    
    parser.add_argument(
        'query',
        help="Your question or code snippet to search for"
    )
    
    parser.add_argument(
        '--top', '-t',
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    
    parser.add_argument(
        '--threshold', '-th',
        type=float,
        default=0.70,
        help="Minimum similarity threshold (default: 0.70)"
    )
    
    parser.add_argument(
        '--stats', '-s',
        action='store_true',
        help="Show Canon statistics before querying"
    )
    
    args = parser.parse_args()
    
    # Initialize query interface
    try:
        query_engine = CanonQuery(similarity_threshold=args.threshold)
        print("✅ Canon query interface initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Canon: {e}")
        sys.exit(1)
    
    # Show statistics if requested
    if args.stats:
        try:
            index_stats = query_engine.pinecone_index.describe_index_stats()
            print(f"\n📊 Canon Statistics:")
            print(f"   Total vectors: {index_stats.get('total_vector_count', 0)}")
            print(f"   Dimension: {index_stats.get('dimension', 0)}")
            print(f"   Index fullness: {index_stats.get('index_fullness', 0):.2%}")
        except Exception as e:
            print(f"⚠️  Could not fetch statistics: {e}")
    
    # Execute query
    results = query_engine.query(args.query, args.top)
    
    # Display results
    query_engine.format_results(results, args.query)

if __name__ == "__main__":
    main()
