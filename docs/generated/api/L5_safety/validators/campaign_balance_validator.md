# API Documentation: campaign_balance_validator

**Target Audience**: developers, api_users

# campaign_balance_validator API Documentation

**File**: `campaign_balance_validator.py`
**Classes**: 2
**Functions**: 8

## Classes

- **BalanceResult**
- **CampaignBalanceValidator**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **validate_campaign_balance** -> BalanceResult
- **_calculate_lead_message_ratio** -> float | None
- **_validate_ratio** -> list[str]
- **_validate_required_fields** -> list[str]
- **calculate_balance_score** -> float
- **suggest_improvements** -> list[str]


## Class: BalanceResult

**Description**: Result of campaign balance validation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: CampaignBalanceValidator

**Description**: 
    Pure deterministic campaign balance validation.

    All logic is 100% deterministic - no external dependencies or LLM calls.
    

### Methods

#### __init__
**Parameters**: self, thresholds
**Returns**: None
**Description**: 
        Initialize with balance validation thresholds.

        Args:
            thresholds: Configuration for balance validation
        

#### validate_campaign_balance
**Parameters**: self, campaign, leads, messages
**Returns**: BalanceResult
**Description**: 
        Validate campaign balance using purely deterministic logic.

        Args:
            campaign: Campaign data dictionary
            leads: List of lead objects
            messages: List of message objects

        Returns:
            BalanceResult with deterministic findings
        

#### _calculate_lead_message_ratio
**Parameters**: self, leads, messages
**Returns**: float | None
**Description**: 
        Calculate lead-to-message ratio using deterministic arithmetic.

        Moved to Deterministic: Pure mathematical calculation
        

#### _validate_ratio
**Parameters**: self, ratio
**Returns**: list[str]
**Description**: 
        Validate ratio against deterministic thresholds.

        Moved to Deterministic: Pure comparison logic
        

#### _validate_required_fields
**Parameters**: self, campaign
**Returns**: list[str]
**Description**: 
        Validate required campaign fields using deterministic checks.

        Moved to Deterministic: Pure existence validation
        

#### calculate_balance_score
**Parameters**: self, campaign, leads, messages
**Returns**: float
**Description**: 
        Calculate overall balance score using deterministic algorithm.

        Returns:
            Float between 0.0 and 1.0 representing balance quality
        

#### suggest_improvements
**Parameters**: self, campaign, leads, messages
**Returns**: list[str]
**Description**: 
        Generate deterministic improvement suggestions.

        Returns:
            List of actionable improvement suggestions
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, thresholds
**Returns**: None
**Description**: 
        Initialize with balance validation thresholds.

        Args:
            thresholds: Configuration for balance validation
        



## Function: validate_campaign_balance

**Parameters**: self, campaign, leads, messages
**Returns**: BalanceResult
**Description**: 
        Validate campaign balance using purely deterministic logic.

        Args:
            campaign: Campaign data dictionary
            leads: List of lead objects
            messages: List of message objects

        Returns:
            BalanceResult with deterministic findings
        



## Function: _calculate_lead_message_ratio

**Parameters**: self, leads, messages
**Returns**: float | None
**Description**: 
        Calculate lead-to-message ratio using deterministic arithmetic.

        Moved to Deterministic: Pure mathematical calculation
        



## Function: _validate_ratio

**Parameters**: self, ratio
**Returns**: list[str]
**Description**: 
        Validate ratio against deterministic thresholds.

        Moved to Deterministic: Pure comparison logic
        



## Function: _validate_required_fields

**Parameters**: self, campaign
**Returns**: list[str]
**Description**: 
        Validate required campaign fields using deterministic checks.

        Moved to Deterministic: Pure existence validation
        



## Function: calculate_balance_score

**Parameters**: self, campaign, leads, messages
**Returns**: float
**Description**: 
        Calculate overall balance score using deterministic algorithm.

        Returns:
            Float between 0.0 and 1.0 representing balance quality
        



## Function: suggest_improvements

**Parameters**: self, campaign, leads, messages
**Returns**: list[str]
**Description**: 
        Generate deterministic improvement suggestions.

        Returns:
            List of actionable improvement suggestions
        



## Usage Examples

### Class Usage

```python
# Using BalanceResult
balanceresult = BalanceResult()
```

```python
# Using CampaignBalanceValidator
campaignbalancevalidator = CampaignBalanceValidator()
campaignbalancevalidator.validate_campaign_balance()
campaignbalancevalidator.calculate_balance_score()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __init__
result = __init__(thresholds)
```

```python
# Using validate_campaign_balance
result = validate_campaign_balance(campaign, leads)
```



---
**Generated**: 2026-03-26T09:39:05.749189
**Type**: api_reference
**Quality**: comprehensive
