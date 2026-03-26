# API Documentation: d0_injection_engine_enforcer

**Target Audience**: developers, api_users

# d0_injection_engine_enforcer API Documentation

**File**: `d0_injection_engine_enforcer.py`
**Classes**: 2
**Functions**: 2

## Classes

- **RoleFence**
- **D0InjectionEngine**

## Functions

- **render_d0** -> str
- **inject** -> str


## Class: RoleFence

**Description**: Immutable role fence for D0 injection.



## Class: D0InjectionEngine

**Description**: 
    Deterministic D0 injection engine for role fences.

    Renders fences in deterministic order with no mutation of input objects.
    

### Methods

#### render_d0
**Parameters**: self
**Returns**: str
**Description**: 
                Render D0 string from role fences.

                Deterministic rendering:
                - Sort fences by fence_id
                - Join as: "<D0>
        [fence_id] text
        ...
        </D0>
        "

                Args:
                    fences: Tuple of RoleFence objects

                Returns:
                    Rendered D0 string
        

#### inject
**Parameters**: self
**Returns**: str
**Description**: 
        Inject D0 fences into payload context.

        Returns the computed D0 string only.
        Does NOT mutate payload_like.
        Does NOT import or depend on L0 types.

        Args:
            payload_like: Object to inject into (not modified)
            fences: Tuple of RoleFence objects

        Returns:
            Rendered D0 string
        



## Function: render_d0

**Parameters**: self
**Returns**: str
**Description**: 
                Render D0 string from role fences.

                Deterministic rendering:
                - Sort fences by fence_id
                - Join as: "<D0>
        [fence_id] text
        ...
        </D0>
        "

                Args:
                    fences: Tuple of RoleFence objects

                Returns:
                    Rendered D0 string
        



## Function: inject

**Parameters**: self
**Returns**: str
**Description**: 
        Inject D0 fences into payload context.

        Returns the computed D0 string only.
        Does NOT mutate payload_like.
        Does NOT import or depend on L0 types.

        Args:
            payload_like: Object to inject into (not modified)
            fences: Tuple of RoleFence objects

        Returns:
            Rendered D0 string
        



## Usage Examples

### Class Usage

```python
# Using RoleFence
rolefence = RoleFence()
```

```python
# Using D0InjectionEngine
d0injectionengine = D0InjectionEngine()
d0injectionengine.render_d0()
d0injectionengine.inject()
```

### Function Usage

```python
# Using render_d0
result = render_d0()
```

```python
# Using inject
result = inject()
```



---
**Generated**: 2026-03-26T09:39:04.801106
**Type**: api_reference
**Quality**: comprehensive
