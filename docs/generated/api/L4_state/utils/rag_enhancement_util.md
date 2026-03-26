# API Documentation: rag_enhancement_util

**Target Audience**: developers, api_users

# rag_enhancement_util API Documentation

**File**: `rag_enhancement_util.py`
**Classes**: 11
**Functions**: 18

## Classes

- **CacheSufficiencyResult**
- **semantic_cache**
- **KnowledgeGap**
- **GapType**
- **SelfRagProcessor**
- **Episode**
- **EpisodicMemory**
- **KgContext**
- **KnowledgeGraphInjector**
- **FewShotExample**
- **FewShotInjector**

## Functions

- **__init__**
- **get** -> Any | None
- **set** -> None
- **check_sufficiency** -> CacheSufficiencyResult
- **__init__**
- **identify_gaps** -> list[KnowledgeGap]
- **should_retrieve_more** -> bool
- **__init__**
- **add_episode** -> None
- **retrieve_relevant** -> list[Episode]
- **__init__**
- **extract_entities** -> list[str]
- **get_context** -> KGContext
- **inject_context** -> str
- **__init__**
- **add_example** -> None
- **get_relevant_examples** -> list[FewShotExample]
- **inject_examples** -> str


## Class: CacheSufficiencyResult

**Description**: Result of cache sufficiency check.



## Class: semantic_cache

**Description**: Semantic cache for LLM responses.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize semantic cache.

#### get
**Parameters**: self, key
**Returns**: Any | None
**Description**: Get cached value by key.

#### set
**Parameters**: self, key, value
**Returns**: None
**Description**: Set cached value.

#### check_sufficiency
**Parameters**: self, query
**Returns**: CacheSufficiencyResult
**Description**: Check if cached response is sufficient for query.



## Class: KnowledgeGap

**Description**: Represents a gap in knowledge.



## Class: GapType

**Description**: Knowledge gap types.



## Class: SelfRagProcessor

**Description**: Self-RAG processor for identifying knowledge gaps.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize self-RAG processor.

#### identify_gaps
**Parameters**: self, query, context
**Returns**: list[KnowledgeGap]
**Description**: Identify knowledge gaps in the context.

#### should_retrieve_more
**Parameters**: self, gaps
**Returns**: bool
**Description**: Determine if more retrieval is needed.



## Class: Episode

**Description**: Represents an episodic memory.



## Class: EpisodicMemory

**Description**: Episodic memory for storing interaction history.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize episodic memory.

#### add_episode
**Parameters**: self, Episode
**Returns**: None
**Description**: Add an Episode to memory.

#### retrieve_relevant
**Parameters**: self, query, top_k
**Returns**: list[Episode]
**Description**: Retrieve relevant episodes.



## Class: KgContext

**Description**: Knowledge graph context.



## Class: KnowledgeGraphInjector

**Description**: Injects knowledge graph context into queries.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize knowledge graph injector.

#### extract_entities
**Parameters**: self, text
**Returns**: list[str]
**Description**: Extract entities from text.

#### get_context
**Parameters**: self, entities
**Returns**: KGContext
**Description**: Get knowledge graph context for entities.

#### inject_context
**Parameters**: self, query, context
**Returns**: str
**Description**: Inject KG context into query.



## Class: FewShotExample

**Description**: Few-shot learning example.



## Class: FewShotInjector

**Description**: Injects few-shot examples into prompts.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize few-shot injector.

#### add_example
**Parameters**: self, example
**Returns**: None
**Description**: Add a few-shot example.

#### get_relevant_examples
**Parameters**: self, query, top_k
**Returns**: list[FewShotExample]
**Description**: Get relevant few-shot examples.

#### inject_examples
**Parameters**: self, prompt, examples
**Returns**: str
**Description**: Inject examples into prompt.



## Function: __init__

**Parameters**: self
**Description**: Initialize semantic cache.



## Function: get

**Parameters**: self, key
**Returns**: Any | None
**Description**: Get cached value by key.



## Function: set

**Parameters**: self, key, value
**Returns**: None
**Description**: Set cached value.



## Function: check_sufficiency

**Parameters**: self, query
**Returns**: CacheSufficiencyResult
**Description**: Check if cached response is sufficient for query.



## Function: __init__

**Parameters**: self
**Description**: Initialize self-RAG processor.



## Function: identify_gaps

**Parameters**: self, query, context
**Returns**: list[KnowledgeGap]
**Description**: Identify knowledge gaps in the context.



## Function: should_retrieve_more

**Parameters**: self, gaps
**Returns**: bool
**Description**: Determine if more retrieval is needed.



## Function: __init__

**Parameters**: self
**Description**: Initialize episodic memory.



## Function: add_episode

**Parameters**: self, Episode
**Returns**: None
**Description**: Add an Episode to memory.



## Function: retrieve_relevant

**Parameters**: self, query, top_k
**Returns**: list[Episode]
**Description**: Retrieve relevant episodes.



## Function: __init__

**Parameters**: self
**Description**: Initialize knowledge graph injector.



## Function: extract_entities

**Parameters**: self, text
**Returns**: list[str]
**Description**: Extract entities from text.



## Function: get_context

**Parameters**: self, entities
**Returns**: KGContext
**Description**: Get knowledge graph context for entities.



## Function: inject_context

**Parameters**: self, query, context
**Returns**: str
**Description**: Inject KG context into query.



## Function: __init__

**Parameters**: self
**Description**: Initialize few-shot injector.



## Function: add_example

**Parameters**: self, example
**Returns**: None
**Description**: Add a few-shot example.



## Function: get_relevant_examples

**Parameters**: self, query, top_k
**Returns**: list[FewShotExample]
**Description**: Get relevant few-shot examples.



## Function: inject_examples

**Parameters**: self, prompt, examples
**Returns**: str
**Description**: Inject examples into prompt.



## Usage Examples

### Class Usage

```python
# Using CacheSufficiencyResult
cachesufficiencyresult = CacheSufficiencyResult()
```

```python
# Using semantic_cache
semantic_cache = semantic_cache()
semantic_cache.get()
semantic_cache.set()
```

```python
# Using KnowledgeGap
knowledgegap = KnowledgeGap()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using get
result = get(key)
```

```python
# Using set
result = set(key, value)
```



---
**Generated**: 2026-03-26T09:39:04.678011
**Type**: api_reference
**Quality**: comprehensive
