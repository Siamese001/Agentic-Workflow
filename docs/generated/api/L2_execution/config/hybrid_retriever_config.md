# API Documentation: hybrid_retriever_config

**Target Audience**: developers, api_users

# hybrid_retriever_config API Documentation

**File**: `hybrid_retriever_config.py`
**Classes**: 6
**Functions**: 14

## Classes

- **ASTAwareTokenizer**
- **RetrievalResult**
- **HybridRetriever**
- **NoOpGuardrail**
- **_InMemoryVectorStore**
- **HybridRetrieverFactory**

## Functions

- **get_hybrid_retriever** -> HybridRetriever
- **split_identifier** -> list[str]
- **tokenize_code** -> list[str]
- **tokenize_query** -> list[str]
- **__init__**
- **sparse_search** -> list[RetrievalResult]
- **deduplicate_by_hash** -> list[RetrievalResult]
- **reciprocal_rank_fusion** -> list[RetrievalResult]
- **_enforce_context_budget** -> list[RetrievalResult]
- **__init__** -> None
- **add_documents** -> None
- **from_in_memory_store** -> HybridRetriever
- **_build_bm25**
- **_sync**


## Class: ASTAwareTokenizer

**Description**: AST-aware tokenizer optimised for code retrieval with configurable boosting.

### Methods

#### split_identifier
**Parameters**: name
**Returns**: list[str]
**Description**: Split CamelCase and snake_case identifiers into sub-tokens.

#### tokenize_code
**Parameters**: cls, text, boost_symbols
**Returns**: list[str]
**Description**: Tokenize code chunk with AST awareness and optional boosting.

#### tokenize_query
**Parameters**: cls, query
**Returns**: list[str]
**Description**: Tokenize natural-language or code query without boosting.



## Class: RetrievalResult

**Description**: Brief description of functionality and purpose.



## Class: HybridRetriever

**Description**: 
    Hybrid retrieval combining semantic search with BM25 sparse retrieval
    

### Methods

#### __init__
**Parameters**: self, vector_store, guardrail

#### sparse_search
**Parameters**: self, query, top_k
**Returns**: list[RetrievalResult]
**Description**: Sparse BM25 search on local chunks

#### deduplicate_by_hash
**Parameters**: self, results, request_seen
**Returns**: list[RetrievalResult]
**Description**: Deduplicate by content hash — prevents redundant chunks

#### reciprocal_rank_fusion
**Parameters**: self, dense, sparse, k
**Returns**: list[RetrievalResult]
**Description**: 
        Fused rankings using optimized RRF (O(N) performance)
        

#### _enforce_context_budget
**Parameters**: self, docs, max_tokens
**Returns**: list[RetrievalResult]
**Description**: P4-4C: Return the longest prefix of *docs* whose cumulative token estimate
        stays within *max_tokens* (default MAX_CONTEXT_TOKENS).

        Token estimate: len(doc.text) // 4 per document (4 chars ≈ 1 token).
        Always includes at least one document to prevent empty-result on large chunks.
        



## Class: NoOpGuardrail

**Description**: Passthrough guardrail: rerank_documents returns candidates[:top_k] unchanged.

    Used by HybridRetrieverFactory for test/dev environments where no
    cross-encoder reranker is available.
    



## Class: _InMemoryVectorStore

**Description**: Minimal in-memory vector store for HybridRetrieverFactory default.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### add_documents
**Parameters**: self, docs
**Returns**: None



## Class: HybridRetrieverFactory

**Description**: Factory for constructing HybridRetriever with injectable dependencies.

### Methods

#### from_in_memory_store
**Parameters**: cls
**Returns**: HybridRetriever
**Description**: Construct a HybridRetriever with InMemoryVectorStore + NoOpGuardrail.

        Allows synchronous construction in tests without an event loop.
        



## Function: get_hybrid_retriever

**Returns**: HybridRetriever
**Description**: Return the process-global HybridRetriever singleton (lazy-initialized).

    Uses HybridRetrieverFactory.from_in_memory_store() on first call.
    Production callers may replace this singleton by assigning to
    ``_hybrid_retriever_singleton`` before first call.
    



## Function: split_identifier

**Parameters**: name
**Returns**: list[str]
**Description**: Split CamelCase and snake_case identifiers into sub-tokens.



## Function: tokenize_code

**Parameters**: cls, text, boost_symbols
**Returns**: list[str]
**Description**: Tokenize code chunk with AST awareness and optional boosting.



## Function: tokenize_query

**Parameters**: cls, query
**Returns**: list[str]
**Description**: Tokenize natural-language or code query without boosting.



## Function: __init__

**Parameters**: self, vector_store, guardrail


## Function: sparse_search

**Parameters**: self, query, top_k
**Returns**: list[RetrievalResult]
**Description**: Sparse BM25 search on local chunks



## Function: deduplicate_by_hash

**Parameters**: self, results, request_seen
**Returns**: list[RetrievalResult]
**Description**: Deduplicate by content hash — prevents redundant chunks



## Function: reciprocal_rank_fusion

**Parameters**: self, dense, sparse, k
**Returns**: list[RetrievalResult]
**Description**: 
        Fused rankings using optimized RRF (O(N) performance)
        



## Function: _enforce_context_budget

**Parameters**: self, docs, max_tokens
**Returns**: list[RetrievalResult]
**Description**: P4-4C: Return the longest prefix of *docs* whose cumulative token estimate
        stays within *max_tokens* (default MAX_CONTEXT_TOKENS).

        Token estimate: len(doc.text) // 4 per document (4 chars ≈ 1 token).
        Always includes at least one document to prevent empty-result on large chunks.
        



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: add_documents

**Parameters**: self, docs
**Returns**: None


## Function: from_in_memory_store

**Parameters**: cls
**Returns**: HybridRetriever
**Description**: Construct a HybridRetriever with InMemoryVectorStore + NoOpGuardrail.

        Allows synchronous construction in tests without an event loop.
        



## Function: _build_bm25



## Function: _sync



## Usage Examples

### Class Usage

```python
# Using ASTAwareTokenizer
astawaretokenizer = ASTAwareTokenizer()
astawaretokenizer.split_identifier()
astawaretokenizer.tokenize_code()
```

```python
# Using RetrievalResult
retrievalresult = RetrievalResult()
```

```python
# Using HybridRetriever
hybridretriever = HybridRetriever()
hybridretriever.sparse_search()
hybridretriever.deduplicate_by_hash()
```

### Function Usage

```python
# Using get_hybrid_retriever
result = get_hybrid_retriever()
```

```python
# Using split_identifier
result = split_identifier(name)
```

```python
# Using tokenize_code
result = tokenize_code(cls, text)
```



---
**Generated**: 2026-03-26T09:39:03.623909
**Type**: api_reference
**Quality**: comprehensive
