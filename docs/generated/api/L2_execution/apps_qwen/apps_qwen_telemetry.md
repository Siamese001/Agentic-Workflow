# API Documentation: apps_qwen_telemetry

**Target Audience**: developers, api_users

# apps_qwen_telemetry API Documentation

**File**: `apps_qwen_telemetry.py`
**Classes**: 3
**Functions**: 8

## Classes

- **AppsQwenMetric**
- **AppsQwenSessionMetrics**
- **AppsQwenTelemetry**

## Functions

- **__init__**
- **start_session** -> str
- **end_session** -> Optional[AppsQwenSessionMetrics]
- **record_request_start** -> None
- **record_request_success** -> None
- **record_request_error** -> None
- **get_session_summary** -> Optional[Dict[str, float]]
- **get_app_summary** -> Dict[str, float]


## Class: AppsQwenMetric

**Description**: Single metric data point.



## Class: AppsQwenSessionMetrics

**Description**: Metrics for a single inference session.



## Class: AppsQwenTelemetry

**Description**: Telemetry collector for apps Qwen operations.

    Tracks performance, usage, and error metrics across all apps.
    

### Methods

#### __init__
**Parameters**: self

#### start_session
**Parameters**: self, app_name
**Returns**: str
**Description**: Start a new telemetry session.

        Args:
            app_name: Name of the app

        Returns:
            Session ID
        

#### end_session
**Parameters**: self, session_id
**Returns**: Optional[AppsQwenSessionMetrics]
**Description**: End a telemetry session and calculate final metrics.

        Args:
            session_id: Session ID to end

        Returns:
            Session metrics if found
        

#### record_request_start
**Parameters**: self, session_id, app_name, model_id
**Returns**: None
**Description**: Record the start of an inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model being used
        

#### record_request_success
**Parameters**: self, session_id, app_name, model_id, latency_ms, confidence, tokens_used
**Returns**: None
**Description**: Record successful inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model used
            latency_ms: Request latency
            confidence: Response confidence
            tokens_used: Tokens consumed
        

#### record_request_error
**Parameters**: self, session_id, app_name, model_id, error_message
**Returns**: None
**Description**: Record failed inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model used
            error_message: Error description
        

#### get_session_summary
**Parameters**: self, session_id
**Returns**: Optional[Dict[str, float]]
**Description**: Get summary metrics for a session.

        Args:
            session_id: Session ID

        Returns:
            Summary metrics dictionary
        

#### get_app_summary
**Parameters**: self, app_name
**Returns**: Dict[str, float]
**Description**: Get aggregated metrics for an app.

        Args:
            app_name: App name

        Returns:
            Aggregated metrics
        



## Function: __init__

**Parameters**: self


## Function: start_session

**Parameters**: self, app_name
**Returns**: str
**Description**: Start a new telemetry session.

        Args:
            app_name: Name of the app

        Returns:
            Session ID
        



## Function: end_session

**Parameters**: self, session_id
**Returns**: Optional[AppsQwenSessionMetrics]
**Description**: End a telemetry session and calculate final metrics.

        Args:
            session_id: Session ID to end

        Returns:
            Session metrics if found
        



## Function: record_request_start

**Parameters**: self, session_id, app_name, model_id
**Returns**: None
**Description**: Record the start of an inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model being used
        



## Function: record_request_success

**Parameters**: self, session_id, app_name, model_id, latency_ms, confidence, tokens_used
**Returns**: None
**Description**: Record successful inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model used
            latency_ms: Request latency
            confidence: Response confidence
            tokens_used: Tokens consumed
        



## Function: record_request_error

**Parameters**: self, session_id, app_name, model_id, error_message
**Returns**: None
**Description**: Record failed inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model used
            error_message: Error description
        



## Function: get_session_summary

**Parameters**: self, session_id
**Returns**: Optional[Dict[str, float]]
**Description**: Get summary metrics for a session.

        Args:
            session_id: Session ID

        Returns:
            Summary metrics dictionary
        



## Function: get_app_summary

**Parameters**: self, app_name
**Returns**: Dict[str, float]
**Description**: Get aggregated metrics for an app.

        Args:
            app_name: App name

        Returns:
            Aggregated metrics
        



## Usage Examples

### Class Usage

```python
# Using AppsQwenMetric
appsqwenmetric = AppsQwenMetric()
```

```python
# Using AppsQwenSessionMetrics
appsqwensessionmetrics = AppsQwenSessionMetrics()
```

```python
# Using AppsQwenTelemetry
appsqwentelemetry = AppsQwenTelemetry()
appsqwentelemetry.start_session()
appsqwentelemetry.end_session()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using start_session
result = start_session(app_name)
```

```python
# Using end_session
result = end_session(session_id)
```



---
**Generated**: 2026-03-26T09:39:03.611998
**Type**: api_reference
**Quality**: comprehensive
