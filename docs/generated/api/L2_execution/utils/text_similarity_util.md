# API Documentation: text_similarity_util

**Target Audience**: developers, api_users

# text_similarity_util API Documentation

**File**: `text_similarity_util.py`
**Classes**: 1
**Functions**: 5

## Classes

- **TextSimilarityCalculator**

## Functions

- **__init__** -> None
- **calculate** -> float
- **_calculate_sklearn** -> float
- **_calculate_fallback** -> float
- **find_duplicates** -> list[tuple[int, int, float]]


## Class: TextSimilarityCalculator

**Description**: Calculate TF-IDF cosine similarity between texts.

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the similarity calculator.

#### calculate
**Parameters**: self, text1, text2
**Returns**: float
**Description**: Calculate cosine similarity between two texts.

#### _calculate_sklearn
**Parameters**: self, text1, text2
**Returns**: float
**Description**: Calculate using scikit-learn TfidfVectorizer.

#### _calculate_fallback
**Parameters**: self, text1, text2
**Returns**: float
**Description**: Basic fallback implementation without sklearn.

#### find_duplicates
**Parameters**: self, texts, threshold
**Returns**: list[tuple[int, int, float]]
**Description**: Find text pairs with similarity >= threshold.



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the similarity calculator.



## Function: calculate

**Parameters**: self, text1, text2
**Returns**: float
**Description**: Calculate cosine similarity between two texts.



## Function: _calculate_sklearn

**Parameters**: self, text1, text2
**Returns**: float
**Description**: Calculate using scikit-learn TfidfVectorizer.



## Function: _calculate_fallback

**Parameters**: self, text1, text2
**Returns**: float
**Description**: Basic fallback implementation without sklearn.



## Function: find_duplicates

**Parameters**: self, texts, threshold
**Returns**: list[tuple[int, int, float]]
**Description**: Find text pairs with similarity >= threshold.



## Usage Examples

### Class Usage

```python
# Using TextSimilarityCalculator
textsimilaritycalculator = TextSimilarityCalculator()
textsimilaritycalculator.calculate()
textsimilaritycalculator.find_duplicates()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using calculate
result = calculate(text1, text2)
```

```python
# Using _calculate_sklearn
result = _calculate_sklearn(text1, text2)
```



---
**Generated**: 2026-03-26T09:39:04.070474
**Type**: api_reference
**Quality**: comprehensive
