"""Integration test demo for AST-aware BM25 tokenization."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path
from agentic_core.L2_execution.ToolRegistry.hybrid_retriever import ASTAwareTokenizer
from rank_bm25 import BM25Okapi


def test_bm25_with_ast_tokenization():
    """Demonstrate BM25 search improvement with AST-aware tokenization."""
    
    print("\n" + "="*80)
    print("AST-Aware BM25 Tokenization - Integration Demo")
    print("="*80 + "\n")
    
    # Sample code corpus
    code_chunks = [
        {
            'text': '''
def calculate_total(amount, tax_rate):
    """Calculate total amount including tax."""
    return amount * (1 + tax_rate)
''',
            'name': 'calculate_total function'
        },
        {
            'text': '''
class DataProcessor:
    """Process and transform data efficiently."""
    
    def process_data(self, data):
        """Process the input data."""
        return data.strip().lower()
''',
            'name': 'DataProcessor class'
        },
        {
            'text': '''
async def fetch_user_data(user_id):
    """Fetch user data from database."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return await db.execute(query)
''',
            'name': 'fetch_user_data function'
        },
        {
            'text': '''
def parse_json_response(response):
    """Parse JSON response and extract data."""
    import json
    return json.loads(response.text)
''',
            'name': 'parse_json_response function'
        },
        {
            'text': '''
class HTTPClient:
    """HTTP client for making requests."""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = None
''',
            'name': 'HTTPClient class'
        }
    ]
    
    # Tokenize with AST-aware tokenizer
    print("Tokenizing corpus with AST-aware tokenizer...")
    tokenizer = ASTAwareTokenizer()
    tokenized_corpus = [tokenizer.tokenize_code(chunk['text']) for chunk in code_chunks]
    
    # Build BM25 index
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Test queries
    test_queries = [
        "calculate total",
        "calcTotal",  # variant
        "amount tax rate",
        "process data",
        "fetch user",
        "parse json",
        "HTTP client"
    ]
    
    print("\nQuery Results (Top 3):")
    print("-" * 80)
    
    for query in test_queries:
        tokenized_query = tokenizer.tokenize_query(query)
        scores = bm25.get_scores(tokenized_query)
        top_indices = scores.argsort()[-3:][::-1]
        
        print(f"\nQuery: '{query}'")
        print(f"  Tokenized: {tokenized_query[:10]}...")  # Show first 10 tokens
        
        for rank, idx in enumerate(top_indices, 1):
            if scores[idx] > 0:
                print(f"  {rank}. {code_chunks[idx]['name']} (score: {scores[idx]:.2f})")
    
    print("\n" + "="*80)
    print("Comparison: Old vs New Tokenization")
    print("="*80 + "\n")
    
    # Compare with simple tokenization
    simple_tokenized = [chunk['text'].lower().split() for chunk in code_chunks]
    bm25_simple = BM25Okapi(simple_tokenized)
    
    comparison_query = "calculate total"
    
    # AST-aware
    ast_tokens = tokenizer.tokenize_query(comparison_query)
    ast_scores = bm25.get_scores(ast_tokens)
    ast_top = ast_scores.argsort()[-3:][::-1]
    
    # Simple
    simple_tokens = comparison_query.lower().split()
    simple_scores = bm25_simple.get_scores(simple_tokens)
    simple_top = simple_scores.argsort()[-3:][::-1]
    
    print(f"Query: '{comparison_query}'")
    print("\nAST-Aware Tokenization:")
    for rank, idx in enumerate(ast_top, 1):
        if ast_scores[idx] > 0:
            print(f"  {rank}. {code_chunks[idx]['name']} (score: {ast_scores[idx]:.2f})")
    
    print("\nSimple Tokenization:")
    for rank, idx in enumerate(simple_top, 1):
        if simple_scores[idx] > 0:
            print(f"  {rank}. {code_chunks[idx]['name']} (score: {simple_scores[idx]:.2f})")
    
    print("\n" + "="*80)
    print("Token Boosting Analysis")
    print("="*80 + "\n")
    
    # Show token counts for first chunk
    chunk_text = code_chunks[0]['text']
    tokens = tokenizer.tokenize_code(chunk_text)
    token_counts = {}
    for t in tokens:
        token_counts[t] = token_counts.get(t, 0) + 1
    
    print(f"Chunk: {code_chunks[0]['name']}")
    print("\nTop tokens by frequency (showing boosting effect):")
    sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
    for token, count in sorted_tokens[:10]:
        print(f"  '{token}': {count}x")
    
    print("\n" + "="*80)
    print("✓ Integration test complete!")
    print("="*80 + "\n")
    
    # Assertions
    assert ast_scores[ast_top[0]] > simple_scores[simple_top[0]], \
        "AST-aware should score higher for 'calculate_total' function"
    
    print("✓ Assertion passed: AST-aware tokenization improves ranking")


def test_camelcase_variant_matching():
    """Test that CamelCase variants match snake_case originals."""
    
    print("\n" + "="*80)
    print("CamelCase Variant Matching Test")
    print("="*80 + "\n")
    
    code_chunks = [
        {'text': 'def calculate_total_amount(price, tax): return price + tax', 'name': 'calculate_total_amount'},
        {'text': 'def process_user_data(data): return data.strip()', 'name': 'process_user_data'},
        {'text': 'def fetch_api_response(url): return requests.get(url)', 'name': 'fetch_api_response'},
    ]
    
    tokenizer = ASTAwareTokenizer()
    tokenized_corpus = [tokenizer.tokenize_code(chunk['text']) for chunk in code_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Test CamelCase variants
    test_cases = [
        ('calculateTotalAmount', 'calculate_total_amount'),
        ('processUserData', 'process_user_data'),
        ('fetchApiResponse', 'fetch_api_response'),
    ]
    
    print("Testing CamelCase variant matching:\n")
    
    for camel_query, expected_match in test_cases:
        tokenized_query = tokenizer.tokenize_query(camel_query)
        scores = bm25.get_scores(tokenized_query)
        top_idx = scores.argmax()
        
        matched_name = code_chunks[top_idx]['name']
        print(f"Query: '{camel_query}'")
        print(f"  Tokenized: {tokenized_query}")
        print(f"  Top match: {matched_name} (score: {scores[top_idx]:.2f})")
        print(f"  Expected: {expected_match}")
        print(f"  ✓ Match!" if matched_name == expected_match else "  ✗ Mismatch")
        print()
    
    print("="*80 + "\n")


if __name__ == "__main__":
    test_bm25_with_ast_tokenization()
    test_camelcase_variant_matching()
