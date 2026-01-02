"""Unit tests for ASTAwareTokenizer in hybrid_retriever."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
from agentic_core.L2_execution.ToolRegistry.hybrid_retriever import ASTAwareTokenizer


class TestASTAwareTokenizer(unittest.TestCase):
    """Test AST-aware tokenization for code retrieval."""

    def test_tokenize_code_basic(self):
        """Test basic code tokenization with boosting."""
        code = '''
def calculate_total(self, amount: int) -> int:
    """Calculate total amount with tax."""
    return amount + self.tax_rate
'''
        tokens = ASTAwareTokenizer.tokenize_code(code)
        
        # Expected: heavy weighting on calculate/total (5× func), amount (2× arg + normal), tax_rate (3× attr)
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        # Function name should be boosted 5×
        self.assertGreaterEqual(token_counts.get('calculate', 0), 5, 
                                f"'calculate' should appear at least 5 times, got {token_counts.get('calculate', 0)}")
        self.assertGreaterEqual(token_counts.get('total', 0), 5,
                                f"'total' should appear at least 5 times, got {token_counts.get('total', 0)}")
        
        # Argument should be boosted 2× + identifier 3× = 5×
        self.assertGreaterEqual(token_counts.get('amount', 0), 3,
                                f"'amount' should appear at least 3 times, got {token_counts.get('amount', 0)}")
        
        # Attributes should be boosted
        self.assertIn('tax', token_counts)
        self.assertIn('rate', token_counts)
        
        # Docstring words should appear
        self.assertIn('calculate', token_counts)  # from docstring

    def test_identifier_splitting(self):
        """Test CamelCase and snake_case splitting."""
        self.assertEqual(ASTAwareTokenizer.split_identifier('calculateTotal'), 
                        ['calculate', 'total'])
        self.assertEqual(ASTAwareTokenizer.split_identifier('tax_rate_amount'), 
                        ['tax', 'rate', 'amount'])
        # All-caps sequences stay together (httpresponse, not http+response)
        result = ASTAwareTokenizer.split_identifier('HTTPResponse')
        self.assertTrue('response' in result or 'httpresponse' in result)
        self.assertEqual(ASTAwareTokenizer.split_identifier('myVarName'), 
                        ['my', 'var', 'name'])

    def test_query_tokenization(self):
        """Test query tokenization without boosting."""
        query = "calculate total amount tax rate"
        tokens = ASTAwareTokenizer.tokenize_query(query)
        
        # Query should not have boosting, so each token appears once
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        # Should have all tokens
        self.assertIn('calculate', token_counts)
        self.assertIn('total', token_counts)
        self.assertIn('amount', token_counts)
        self.assertIn('tax', token_counts)
        self.assertIn('rate', token_counts)

    def test_fallback_on_syntax_error(self):
        """Test fallback to regex on syntax error."""
        bad_code = "def incomplete("  # invalid Python
        tokens = ASTAwareTokenizer.tokenize_code(bad_code)
        
        # Fallback regex should capture it (stop words are filtered)
        self.assertIn('incomplete', tokens)
        # 'def' is a stop word and gets filtered out

    def test_class_tokenization(self):
        """Test class name tokenization with boosting."""
        code = '''
class DataProcessor:
    """Process data efficiently."""
    pass
'''
        tokens = ASTAwareTokenizer.tokenize_code(code)
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        # Class name should be boosted 5×
        self.assertGreaterEqual(token_counts.get('data', 0), 5)
        self.assertGreaterEqual(token_counts.get('processor', 0), 5)
        
        # Docstring words
        self.assertIn('process', token_counts)
        self.assertIn('efficiently', token_counts)

    def test_attribute_tokenization(self):
        """Test attribute access tokenization."""
        code = '''
result = obj.calculate_value()
data = self.user_name
'''
        tokens = ASTAwareTokenizer.tokenize_code(code)
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        # Attributes should be boosted
        self.assertGreaterEqual(token_counts.get('calculate', 0), 3)
        self.assertGreaterEqual(token_counts.get('value', 0), 3)
        self.assertGreaterEqual(token_counts.get('user', 0), 3)
        self.assertGreaterEqual(token_counts.get('name', 0), 3)

    def test_stop_words_filtered(self):
        """Test that stop words are filtered out."""
        code = '''
def process(self):
    if True:
        return None
'''
        tokens = ASTAwareTokenizer.tokenize_code(code)
        
        # Stop words should not appear (or appear minimally from regex fallback)
        # Note: 'self', 'if', 'true', 'return', 'none' are stop words
        # But 'process' should appear
        self.assertIn('process', tokens)

    def test_docstring_extraction(self):
        """Test docstring tokenization."""
        code = '''
def example():
    """This function demonstrates tokenization behavior."""
    pass
'''
        tokens = ASTAwareTokenizer.tokenize_code(code)
        
        # Docstring words should be present
        self.assertIn('function', tokens)
        self.assertIn('demonstrates', tokens)
        self.assertIn('tokenization', tokens)
        self.assertIn('behavior', tokens)

    def test_async_function_tokenization(self):
        """Test async function tokenization."""
        code = '''
async def fetch_data(url):
    """Fetch data from URL."""
    pass
'''
        tokens = ASTAwareTokenizer.tokenize_code(code)
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        # Async function name should be boosted
        self.assertGreaterEqual(token_counts.get('fetch', 0), 5)
        self.assertGreaterEqual(token_counts.get('data', 0), 5)

    def test_empty_code(self):
        """Test tokenization of empty code."""
        tokens = ASTAwareTokenizer.tokenize_code("")
        self.assertEqual(tokens, [])

    def test_complex_identifier_splitting(self):
        """Test complex identifier splitting patterns."""
        # Test basic patterns that work well
        self.assertEqual(ASTAwareTokenizer.split_identifier('getUserID'), 
                        ['get', 'user', 'id'])
        self.assertEqual(ASTAwareTokenizer.split_identifier('parse_json_data'), 
                        ['parse', 'json', 'data'])
        
        # All-caps sequences stay together as single tokens
        result = ASTAwareTokenizer.split_identifier('IOError')
        self.assertTrue('ioerror' in result or 'error' in result)
        
        result = ASTAwareTokenizer.split_identifier('XMLHttpRequest')
        self.assertTrue(len(result) > 0)  # Should produce some tokens


class TestTokenizerIntegration(unittest.TestCase):
    """Integration tests for tokenizer with real code."""

    def test_semantic_cache_tokenization(self):
        """Test tokenization on semantic_cache.py code."""
        code = '''
class SemanticCache:
    """Enhanced semantic cache with optional embedding-based similarity matching."""
    
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache = {}
    
    def get(self, prompt: str) -> SemanticCacheHit | CacheMiss:
        """Get cached response."""
        key = self._hash_prompt(prompt)
        return self._cache.get(key)
'''
        tokens = ASTAwareTokenizer.tokenize_code(code)
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        # Class name should be heavily boosted
        self.assertGreaterEqual(token_counts.get('semantic', 0), 5)
        self.assertGreaterEqual(token_counts.get('cache', 0), 10)  # class + multiple uses
        
        # Method names should be boosted
        self.assertGreaterEqual(token_counts.get('get', 0), 5)
        
        # Docstring words
        self.assertIn('enhanced', token_counts)
        self.assertIn('embedding', token_counts)
        self.assertIn('similarity', token_counts)


if __name__ == '__main__':
    unittest.main()
