# API Documentation: egress_util

**Target Audience**: developers, api_users

# egress_util API Documentation

**File**: `egress_util.py`
**Classes**: 2
**Functions**: 8

## Classes

- **EgressResult**
- **NetworkingUtility**

## Functions

- **get_networking_utility** -> NetworkingUtility
- **strict_egress_filter** -> EgressResult
- **send_email** -> dict
- **__init__**
- **strict_egress_filter** -> EgressResult
- **send_email** -> dict
- **fetch_url** -> dict
- **get_stats** -> dict


## Class: EgressResult

**Description**: Result from egress filter check.



## Class: NetworkingUtility

**Description**: Provides networking utilities with P8 Egress Filter enforcement.

### Methods

#### __init__
**Parameters**: self, allowed_hosts
**Description**: 
        Initialize networking utility.

        Args:
            allowed_hosts: Set of whitelisted hosts/domains
        

#### strict_egress_filter
**Parameters**: self, url, allowed
**Returns**: EgressResult
**Description**: 
        Check if URL is allowed by egress filter.

        Args:
            url: URL to check
            allowed: Optional override for allowed hosts

        Returns:
            EgressResult with status and reason
        

#### send_email
**Parameters**: self, to, subject, body, send_time, dry_run
**Returns**: dict
**Description**: 
        Send email with P8 enforcement.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            send_time: Optional scheduled send time
            dry_run: If True, only log without sending

        Returns:
            Send result with status
        

#### fetch_url
**Parameters**: self, url, headers
**Returns**: dict
**Description**: 
        Fetch URL content with P8 enforcement via MCP fetch tool.

        Routes through mcp4_fetch (MCP fetch server) for all outbound HTTP.
        Egress filter is enforced before any network call is attempted.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Fetch result with content or error
        

#### get_stats
**Parameters**: self
**Returns**: dict
**Description**: Get egress filter statistics.



## Function: get_networking_utility

**Parameters**: allowed_hosts
**Returns**: NetworkingUtility
**Description**: Get singleton networking utility instance.



## Function: strict_egress_filter

**Parameters**: url, allowed
**Returns**: EgressResult
**Description**: Convenience function for egress filter check.



## Function: send_email

**Parameters**: to, subject, body, send_time, dry_run
**Returns**: dict
**Description**: Convenience function for sending email.



## Function: __init__

**Parameters**: self, allowed_hosts
**Description**: 
        Initialize networking utility.

        Args:
            allowed_hosts: Set of whitelisted hosts/domains
        



## Function: strict_egress_filter

**Parameters**: self, url, allowed
**Returns**: EgressResult
**Description**: 
        Check if URL is allowed by egress filter.

        Args:
            url: URL to check
            allowed: Optional override for allowed hosts

        Returns:
            EgressResult with status and reason
        



## Function: send_email

**Parameters**: self, to, subject, body, send_time, dry_run
**Returns**: dict
**Description**: 
        Send email with P8 enforcement.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            send_time: Optional scheduled send time
            dry_run: If True, only log without sending

        Returns:
            Send result with status
        



## Function: fetch_url

**Parameters**: self, url, headers
**Returns**: dict
**Description**: 
        Fetch URL content with P8 enforcement via MCP fetch tool.

        Routes through mcp4_fetch (MCP fetch server) for all outbound HTTP.
        Egress filter is enforced before any network call is attempted.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Fetch result with content or error
        



## Function: get_stats

**Parameters**: self
**Returns**: dict
**Description**: Get egress filter statistics.



## Usage Examples

### Class Usage

```python
# Using EgressResult
egressresult = EgressResult()
```

```python
# Using NetworkingUtility
networkingutility = NetworkingUtility()
networkingutility.strict_egress_filter()
networkingutility.send_email()
```

### Function Usage

```python
# Using get_networking_utility
result = get_networking_utility(allowed_hosts)
```

```python
# Using strict_egress_filter
result = strict_egress_filter(url, allowed)
```

```python
# Using send_email
result = send_email(to, subject)
```



---
**Generated**: 2026-03-26T09:39:04.060520
**Type**: api_reference
**Quality**: comprehensive
