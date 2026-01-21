"""Test tree-sitter-languages API to find correct usage."""

from tree_sitter import Parser
from tree_sitter_languages import get_language

# Get language
lang = get_language("python")
print(f"Language type: {type(lang)}")
print(f"Language: {lang}")

# Create parser
p = Parser()
print(f"\nParser type: {type(p)}")
print(f"Parser methods: {[m for m in dir(p) if not m.startswith('_')]}")

# Try different ways to set language
try:
    p.language = lang
    print("\n✓ p.language = lang works!")
except Exception as e:
    print(f"\n✗ p.language = lang failed: {e}")

try:
    p.set_language(lang)
    print("✓ p.set_language(lang) works!")
except Exception as e:
    print(f"✗ p.set_language(lang) failed: {e}")

# Test parsing
if p.language:
    code = b"def foo():\n    return 42"
    tree = p.parse(code)
    print("\n✓ Parsing successful!")
    print(f"Root node type: {tree.root_node.type}")
