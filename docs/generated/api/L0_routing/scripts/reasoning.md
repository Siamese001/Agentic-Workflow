# API Documentation: reasoning

**Target Audience**: developers, api_users

# reasoning API Documentation

**File**: `reasoning.py`
**Classes**: 8
**Functions**: 12

## Classes

- **ReasoningStrategy** (inherits from ABC)
- **ChainOfThoughtStrategy** (inherits from ReasoningStrategy)
- **TreeOfThoughtsStrategy** (inherits from ReasoningStrategy)
- **ReActStrategy** (inherits from ReasoningStrategy)
- **ReflectionStrategy** (inherits from ReasoningStrategy)
- **CritiqueStrategy** (inherits from ReasoningStrategy)
- **MultiPathStrategy** (inherits from ReasoningStrategy)
- **ReasoningStrategyFactory**

## Functions

- **__init__**
- **execute** -> list[str]
- **_validate_input** -> bool
- **execute** -> list[str]
- **execute** -> list[str]
- **execute** -> list[str]
- **execute** -> list[str]
- **execute** -> list[str]
- **execute** -> list[str]
- **create** -> ReasoningStrategy
- **register** -> None
- **available_strategies** -> list[str]


## Class: ReasoningStrategy

**Description**: Base strategy for polymorphic reasoning execution.

**Inherits from**: ABC

### Methods

#### __init__
**Parameters**: self, max_steps, config
**Description**: 
        Initialize reasoning strategy.

        Args:
            max_steps: Maximum reasoning steps
            config: Strategy-specific configuration
        

#### execute
**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: 
        Execute reasoning strategy.

        Args:
            problem: Problem statement
            context: Execution context with state

        Returns:
            List of reasoning steps
        

#### _validate_input
**Parameters**: self, problem, context
**Returns**: bool
**Description**: Validate inputs before execution.



## Class: ChainOfThoughtStrategy

**Description**: Chain of Thought (CoT) reasoning - sequential step-by-step.

**Inherits from**: ReasoningStrategy

### Methods

#### execute
**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute CoT reasoning.



## Class: TreeOfThoughtsStrategy

**Description**: Tree of Thoughts (ToT) reasoning - branching exploration.

**Inherits from**: ReasoningStrategy

### Methods

#### execute
**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute ToT reasoning with branching.



## Class: ReActStrategy

**Description**: ReAct (Reasoning + Acting) - interleaved reasoning and action.

**Inherits from**: ReasoningStrategy

### Methods

#### execute
**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute ReAct reasoning with actions.



## Class: ReflectionStrategy

**Description**: Reflection reasoning - self-critique and refinement.

**Inherits from**: ReasoningStrategy

### Methods

#### execute
**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute reflection reasoning.



## Class: CritiqueStrategy

**Description**: Critique reasoning - adversarial evaluation.

**Inherits from**: ReasoningStrategy

### Methods

#### execute
**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute critique reasoning.



## Class: MultiPathStrategy

**Description**: Multi-path reasoning - parallel exploration.

**Inherits from**: ReasoningStrategy

### Methods

#### execute
**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute multi-path reasoning.



## Class: ReasoningStrategyFactory

**Description**: Factory for creating reasoning strategies.

### Methods

#### create
**Parameters**: cls, strategy_type, max_steps, config
**Returns**: ReasoningStrategy
**Description**: 
        Create reasoning strategy instance.

        Args:
            strategy_type: Type of strategy (cot, tot, react, etc.)
            max_steps: Maximum reasoning steps
            config: Strategy-specific configuration

        Returns:
            ReasoningStrategy instance

        Raises:
            ValueError: If strategy type unknown
        

#### register
**Parameters**: cls, name, strategy_class
**Returns**: None
**Description**: Register custom strategy.

#### available_strategies
**Parameters**: cls
**Returns**: list[str]
**Description**: Get list of available strategies.



## Function: __init__

**Parameters**: self, max_steps, config
**Description**: 
        Initialize reasoning strategy.

        Args:
            max_steps: Maximum reasoning steps
            config: Strategy-specific configuration
        



## Function: execute

**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: 
        Execute reasoning strategy.

        Args:
            problem: Problem statement
            context: Execution context with state

        Returns:
            List of reasoning steps
        



## Function: _validate_input

**Parameters**: self, problem, context
**Returns**: bool
**Description**: Validate inputs before execution.



## Function: execute

**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute CoT reasoning.



## Function: execute

**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute ToT reasoning with branching.



## Function: execute

**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute ReAct reasoning with actions.



## Function: execute

**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute reflection reasoning.



## Function: execute

**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute critique reasoning.



## Function: execute

**Parameters**: self, problem, context
**Returns**: list[str]
**Description**: Execute multi-path reasoning.



## Function: create

**Parameters**: cls, strategy_type, max_steps, config
**Returns**: ReasoningStrategy
**Description**: 
        Create reasoning strategy instance.

        Args:
            strategy_type: Type of strategy (cot, tot, react, etc.)
            max_steps: Maximum reasoning steps
            config: Strategy-specific configuration

        Returns:
            ReasoningStrategy instance

        Raises:
            ValueError: If strategy type unknown
        



## Function: register

**Parameters**: cls, name, strategy_class
**Returns**: None
**Description**: Register custom strategy.



## Function: available_strategies

**Parameters**: cls
**Returns**: list[str]
**Description**: Get list of available strategies.



## Usage Examples

### Class Usage

```python
# Using ReasoningStrategy
reasoningstrategy = ReasoningStrategy()
reasoningstrategy.execute()
```

```python
# Using ChainOfThoughtStrategy
chainofthoughtstrategy = ChainOfThoughtStrategy()
chainofthoughtstrategy.execute()
```

```python
# Using TreeOfThoughtsStrategy
treeofthoughtsstrategy = TreeOfThoughtsStrategy()
treeofthoughtsstrategy.execute()
```

### Function Usage

```python
# Using __init__
result = __init__(max_steps, config)
```

```python
# Using execute
result = execute(problem, context)
```

```python
# Using _validate_input
result = _validate_input(problem, context)
```



---
**Generated**: 2026-03-26T09:39:03.186351
**Type**: api_reference
**Quality**: comprehensive
