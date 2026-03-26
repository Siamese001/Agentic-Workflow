# API Documentation: write_governor_mixin

**Target Audience**: developers, api_users

# write_governor_mixin API Documentation

**File**: `write_governor_mixin.py`
**Classes**: 1
**Functions**: 8

## Classes

- **WriteGovernorMixin**

## Functions

- **_get_uwg** -> UniversalWriteGateway
- **set_write_gateway** -> None
- **governed_write** -> SimulationResult | MutationRecord
- **governed_append** -> SimulationResult | MutationRecord
- **governed_delete** -> SimulationResult | MutationRecord
- **governed_rename** -> SimulationResult | MutationRecord
- **assert_write_governed** -> bool
- **get_write_stats** -> dict[str, Any]


## Class: WriteGovernorMixin

**Description**: Mixin that routes all writes through the UniversalWriteGateway.

    Usage::

        class MyAgent(WriteGovernorMixin, SovereignBaseAgent):
            def do_work(self) -> None:
                self.governed_write("artifacts/output.json", b"{}")

    The mixin resolves the gateway lazily on first use, so subclass
    ``__init__`` need not call anything special.
    

### Methods

#### _get_uwg
**Parameters**: self
**Returns**: UniversalWriteGateway
**Description**: Return the active UWG instance, creating a default one if needed.

#### set_write_gateway
**Parameters**: self, gateway
**Returns**: None
**Description**: Inject a custom gateway (primarily for testing).

#### governed_write
**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Write *data* to *path* via the UWG sovereign gate.

        Raises:
            ToolNotAllowedError: if the path/extension is blocked by the UWG.
        

#### governed_append
**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Append *data* to *path* via the UWG sovereign gate.

#### governed_delete
**Parameters**: self, path
**Returns**: SimulationResult | MutationRecord
**Description**: Delete *path* via the UWG sovereign gate.

#### governed_rename
**Parameters**: self, src, dst
**Returns**: SimulationResult | MutationRecord
**Description**: Rename *src* → *dst* via the UWG sovereign gate.

#### assert_write_governed
**Parameters**: self, path, operation
**Returns**: bool
**Description**: Assert that *path* is in the UWG allowed set without performing a write.

        Returns True if permitted, raises ToolNotAllowedError if blocked.
        

#### get_write_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Proxy to UWG write statistics.



## Function: _get_uwg

**Parameters**: self
**Returns**: UniversalWriteGateway
**Description**: Return the active UWG instance, creating a default one if needed.



## Function: set_write_gateway

**Parameters**: self, gateway
**Returns**: None
**Description**: Inject a custom gateway (primarily for testing).



## Function: governed_write

**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Write *data* to *path* via the UWG sovereign gate.

        Raises:
            ToolNotAllowedError: if the path/extension is blocked by the UWG.
        



## Function: governed_append

**Parameters**: self, path, data
**Returns**: SimulationResult | MutationRecord
**Description**: Append *data* to *path* via the UWG sovereign gate.



## Function: governed_delete

**Parameters**: self, path
**Returns**: SimulationResult | MutationRecord
**Description**: Delete *path* via the UWG sovereign gate.



## Function: governed_rename

**Parameters**: self, src, dst
**Returns**: SimulationResult | MutationRecord
**Description**: Rename *src* → *dst* via the UWG sovereign gate.



## Function: assert_write_governed

**Parameters**: self, path, operation
**Returns**: bool
**Description**: Assert that *path* is in the UWG allowed set without performing a write.

        Returns True if permitted, raises ToolNotAllowedError if blocked.
        



## Function: get_write_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Proxy to UWG write statistics.



## Usage Examples

### Class Usage

```python
# Using WriteGovernorMixin
writegovernormixin = WriteGovernorMixin()
writegovernormixin.set_write_gateway()
writegovernormixin.governed_write()
```

### Function Usage

```python
# Using _get_uwg
result = _get_uwg()
```

```python
# Using set_write_gateway
result = set_write_gateway(gateway)
```

```python
# Using governed_write
result = governed_write(path, data)
```



---
**Generated**: 2026-03-26T09:39:03.746218
**Type**: api_reference
**Quality**: comprehensive
