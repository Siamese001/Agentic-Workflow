# API Documentation: credential_access_guard

**Target Audience**: developers, api_users

# credential_access_guard API Documentation

**File**: `credential_access_guard.py`
**Classes**: 2
**Functions**: 8

## Classes

- **CredentialAccessDenied** (inherits from PermissionError)
- **CredentialAccessGuard**

## Functions

- **_import_secret_access**
- **__init__** -> None
- **guarded_get_secret** -> str
- **guarded_get_env** -> str | None
- **guarded_access_credential** -> Any
- **hash_credential** -> str
- **access_report**
- **_apply_policy_gate** -> None


## Class: CredentialAccessDenied

**Description**: Raised when the guard denies a credential access attempt.

**Inherits from**: PermissionError



## Class: CredentialAccessGuard

**Description**: Safety-plane gate for all credential and secret access.

    Usage::

        guard = CredentialAccessGuard(agent_id="MyAgent", run_id="run-abc")
        api_key = guard.guarded_get_secret("OPENAI_API_KEY")
        db_pass = guard.guarded_get_env("DB_PASSWORD")

    The guard maintains an internal ``SecretAccessRecorder`` and emits a
    ``validated_by_safety_plane`` audit event for each access.
    

### Methods

#### __init__
**Parameters**: self, agent_id, run_id, policy_enforced, denied_prefixes
**Returns**: None

#### guarded_get_secret
**Parameters**: self, secret_name, kind, default
**Returns**: str
**Description**: Retrieve a secret value through the safety-plane gate.

        Args:
            secret_name: The identifier for the secret (e.g. ``OPENAI_API_KEY``).
            kind: The ``SecretKind`` category for audit classification.
            default: Fallback value when the secret is absent (avoid for sensitive data).

        Returns:
            The secret string.

        Raises:
            CredentialAccessDenied: if policy blocks this secret name.
            KeyError: if secret absent and no default provided.
        

#### guarded_get_env
**Parameters**: self, var_name, kind, default
**Returns**: str | None
**Description**: Retrieve an environment variable through the safety-plane gate.

        Unlike ``guarded_get_secret``, missing variables return *default*
        (which may be None) rather than raising.
        

#### guarded_access_credential
**Parameters**: self, credential_name, kind, resolver
**Returns**: Any
**Description**: Access a structured credential through the safety-plane gate.

        Args:
            credential_name: Logical credential identifier.
            kind: Credential kind for audit classification.
            resolver: Optional callable ``(name: str) -> Any`` to retrieve the
                      credential from a vault or credential store.  If None, falls
                      back to ``os.environ``.

        Returns:
            The resolved credential value.

        Raises:
            CredentialAccessDenied: if policy blocks this credential.
        

#### hash_credential
**Parameters**: self, raw_value
**Returns**: str
**Description**: Return a masked SHA-256 hash of a credential value (first 16 hex chars).

#### access_report
**Parameters**: self
**Description**: Return the accumulated ``SecretAccessReport`` for this guard instance.

#### _apply_policy_gate
**Parameters**: self, name
**Returns**: None
**Description**: Raise CredentialAccessDenied if the name violates policy.



## Function: _import_secret_access

**Description**: Lazy import helper — defers L_TOOLS import to call time.



## Function: __init__

**Parameters**: self, agent_id, run_id, policy_enforced, denied_prefixes
**Returns**: None


## Function: guarded_get_secret

**Parameters**: self, secret_name, kind, default
**Returns**: str
**Description**: Retrieve a secret value through the safety-plane gate.

        Args:
            secret_name: The identifier for the secret (e.g. ``OPENAI_API_KEY``).
            kind: The ``SecretKind`` category for audit classification.
            default: Fallback value when the secret is absent (avoid for sensitive data).

        Returns:
            The secret string.

        Raises:
            CredentialAccessDenied: if policy blocks this secret name.
            KeyError: if secret absent and no default provided.
        



## Function: guarded_get_env

**Parameters**: self, var_name, kind, default
**Returns**: str | None
**Description**: Retrieve an environment variable through the safety-plane gate.

        Unlike ``guarded_get_secret``, missing variables return *default*
        (which may be None) rather than raising.
        



## Function: guarded_access_credential

**Parameters**: self, credential_name, kind, resolver
**Returns**: Any
**Description**: Access a structured credential through the safety-plane gate.

        Args:
            credential_name: Logical credential identifier.
            kind: Credential kind for audit classification.
            resolver: Optional callable ``(name: str) -> Any`` to retrieve the
                      credential from a vault or credential store.  If None, falls
                      back to ``os.environ``.

        Returns:
            The resolved credential value.

        Raises:
            CredentialAccessDenied: if policy blocks this credential.
        



## Function: hash_credential

**Parameters**: self, raw_value
**Returns**: str
**Description**: Return a masked SHA-256 hash of a credential value (first 16 hex chars).



## Function: access_report

**Parameters**: self
**Description**: Return the accumulated ``SecretAccessReport`` for this guard instance.



## Function: _apply_policy_gate

**Parameters**: self, name
**Returns**: None
**Description**: Raise CredentialAccessDenied if the name violates policy.



## Usage Examples

### Class Usage

```python
# Using CredentialAccessDenied
credentialaccessdenied = CredentialAccessDenied()
```

```python
# Using CredentialAccessGuard
credentialaccessguard = CredentialAccessGuard()
credentialaccessguard.guarded_get_secret()
credentialaccessguard.guarded_get_env()
```

### Function Usage

```python
# Using _import_secret_access
result = _import_secret_access()
```

```python
# Using __init__
result = __init__(agent_id, run_id)
```

```python
# Using guarded_get_secret
result = guarded_get_secret(secret_name, kind)
```



---
**Generated**: 2026-03-26T09:39:06.013209
**Type**: api_reference
**Quality**: comprehensive
