# API Documentation: job_analyzer_impl

**Target Audience**: developers, api_users

# job_analyzer_impl API Documentation

**File**: `job_analyzer_impl.py`
**Classes**: 1
**Functions**: 7

## Classes

- **JobAnalyzer**

## Functions

- **__init__** -> None
- **analyze** -> dict[str, Any]
- **_build_analysis_prompt** -> str
- **_generate_with_gemini** -> str
- **_generate_with_generic_client** -> str
- **_parse_analysis_response** -> dict[str, Any]
- **extract_keywords** -> list[str]


## Class: JobAnalyzer

**Description**: Analyzes job descriptions using LLM to extract key information.



## Function: __init__

**Parameters**: self, llm_client, Provider, workflow_config
**Returns**: None
**Description**: 
    Initialize JobAnalyzer.

    Args:
        llm_client: Optional pre-configured LLM client
        Provider: Provider to use if client not supplied (defaults to Google/Gemini)
    



## Function: analyze

**Parameters**: self, JobDescription
**Returns**: dict[str, Any]
**Description**: 
    Analyze a job description to extract key information.

    Args:
        JobDescription: Raw job description text

    Returns:
        Dictionary containing:
        - hard_skills: List of required hard skills
        - soft_skills: List of required soft skills
        - key_responsibilities: List of main responsibilities
        - experience_level: Required experience level
        - cultural_indicators: List of cultural fit keywords
        - north_star_metric: Key success Metric for the role
    



## Function: _build_analysis_prompt

**Parameters**: self, JobDescription
**Returns**: str
**Description**: Build the prompt for job analysis.



## Function: _generate_with_gemini

**Parameters**: self, prompt, temperature
**Returns**: str
**Description**: Generate response using Google Gemini.



## Function: _generate_with_generic_client

**Parameters**: self, prompt, temperature
**Returns**: str
**Description**: Generate response using generic client interface.



## Function: _parse_analysis_response

**Parameters**: self, response
**Returns**: dict[str, Any]
**Description**: Parse the LLM response into structured data.



## Function: extract_keywords

**Parameters**: self, JobDescription, max_keywords
**Returns**: list[str]
**Description**: 
    Extract important keywords from job description.

    Args:
        JobDescription: Raw job description text
        max_keywords: Maximum number of keywords to return

    Returns:
        List of relevant keywords
    



## Usage Examples

### Class Usage

```python
# Using JobAnalyzer
jobanalyzer = JobAnalyzer()
```

### Function Usage

```python
# Using __init__
result = __init__(llm_client, Provider)
```

```python
# Using analyze
result = analyze(JobDescription)
```

```python
# Using _build_analysis_prompt
result = _build_analysis_prompt(JobDescription)
```



---
**Generated**: 2026-03-26T09:39:03.910962
**Type**: api_reference
**Quality**: comprehensive
