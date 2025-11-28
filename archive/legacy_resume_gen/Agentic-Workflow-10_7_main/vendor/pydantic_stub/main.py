"""Minimal Pydantic-like shim tailored for the agentic workflow tests."""
from __future__ import annotations

import json
import inspect
from collections.abc import Mapping
from typing import Any, Dict, Iterable, List, Tuple, Type, Union, get_args, get_origin


_UNSET = object()


class ValidationError(Exception):
    """Pydantic-style validation error container."""

    def __init__(self, errors: List[Dict[str, Any]]):
        self._errors = [
            {
                "loc": list(error.get("loc", [])),
                "msg": error.get("msg", ""),
                "type": error.get("type", "value_error"),
            }
            for error in errors
        ]
        message = "; ".join(error["msg"] for error in self._errors)
        super().__init__(message)

    def errors(self) -> List[Dict[str, Any]]:
        return self._errors


def _error(loc: Tuple[Any, ...], msg: str, type_: str) -> Dict[str, Any]:
    return {"loc": list(loc), "msg": msg, "type": type_}


class FieldInfo:
    __slots__ = ("annotation", "default", "default_factory", "metadata")

    def __init__(self, default: Any = _UNSET, *, default_factory=None, **metadata: Any) -> None:
        if default is not _UNSET and default_factory is not None:
            raise ValueError("default and default_factory cannot be used together")
        if default_factory is not None and not callable(default_factory):
            raise TypeError("default_factory must be callable")
        self.annotation = Any
        self.default = default
        self.default_factory = default_factory
        self.metadata = metadata

    @property
    def is_required(self) -> bool:
        return self.default is _UNSET and self.default_factory is None


def Field(default: Any = _UNSET, *, default_factory=None, **metadata: Any) -> FieldInfo:
    return FieldInfo(default=default, default_factory=default_factory, **metadata)


def ConfigDict(**kwargs: Any) -> Dict[str, Any]:
    return dict(kwargs)


class BaseModelMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, dict(namespace))
        cls.__fields__ = mcls._collect_fields(cls, bases)
        cls.__config__ = mcls._build_config(cls, bases)
        return cls

    @staticmethod
    def _build_config(cls, bases):
        config = {
            "extra": "ignore",
            "arbitrary_types_allowed": False,
            "validate_assignment": False,
        }
        config_cls = getattr(cls, "Config", None)
        if config_cls is None:
            for base in bases:
                if hasattr(base, "__config__"):
                    config.update(getattr(base, "__config__"))
                    break
            return config
        for key in ("extra", "arbitrary_types_allowed", "validate_assignment"):
            if hasattr(config_cls, key):
                config[key] = getattr(config_cls, key)
        return config

    @staticmethod
    def _collect_fields(cls, bases):
        fields = {}
        annotations = {}
        for base in reversed(bases):
            annotations.update(getattr(base, "__annotations__", {}))
            fields.update(getattr(base, "__fields__", {}))
        annotations.update(getattr(cls, "__annotations__", {}))
        for name, annotation in annotations.items():
            default = getattr(cls, name, _UNSET)
            if isinstance(default, FieldInfo):
                field_info = default
                if field_info.default is not _UNSET:
                    setattr(cls, name, field_info.default)
                else:
                    if hasattr(cls, name):
                        delattr(cls, name)
            elif default is _UNSET:
                field_info = FieldInfo()
            else:
                field_info = FieldInfo(default=default)
            field_info.annotation = annotation
            fields[name] = field_info
        return fields


class BaseModel(metaclass=BaseModelMeta):
    __fields__: Dict[str, FieldInfo] = {}
    __config__: Dict[str, Any] = {
        "extra": "ignore",
        "arbitrary_types_allowed": False,
        "validate_assignment": False,
    }

    def __init__(self, **data: Any) -> None:
        input_data = dict(data)
        values = {}
        errors: List[Dict[str, Any]] = []
        for name, field in self.__fields__.items():
            raw_value = input_data.pop(name, _UNSET)
            if raw_value is _UNSET:
                if field.default is not _UNSET:
                    value = field.default
                elif field.default_factory is not None:
                    value = field.default_factory()
                else:
                    errors.append(_error((name,), "field required", "value_error.missing"))
                    continue
            else:
                try:
                    value = _validate_type(raw_value, field.annotation, (name,), self.__config__)
                except ValidationError as exc:
                    errors.extend(exc.errors())
                    continue
            values[name] = value
        extra_behavior = self.__config__.get("extra", "ignore")
        if extra_behavior not in {"allow", "ignore", "forbid"}:
            extra_behavior = "ignore"
        if input_data:
            if extra_behavior == "forbid":
                for key in sorted(input_data):
                    errors.append(_error((key,), "extra fields not permitted", "value_error.extra"))
            elif extra_behavior == "allow":
                values.update(input_data)
        if errors:
            raise ValidationError(errors)
        self.__dict__.update(values)

    @classmethod
    def parse_obj(cls: Type["BaseModel"], obj: Any) -> "BaseModel":
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, str):
            try:
                obj = json.loads(obj)
            except json.JSONDecodeError as exc:
                raise ValidationError(
                    [_error((), f"Invalid JSON: {exc.msg}", "value_error.jsondecode")]
                ) from None
        if not isinstance(obj, Mapping):
            raise ValidationError([_error((), "value is not a valid dict", "type_error.dict")])
        return cls(**dict(obj))

    @classmethod
    def model_validate(cls, obj: Any) -> "BaseModel":
        return cls.parse_obj(obj)

    def dict(self) -> Dict[str, Any]:
        result = {}
        for name in self.__fields__:
            if hasattr(self, name):
                result[name] = _serialize_value(getattr(self, name))
        if self.__config__.get("extra") == "allow":
            for key, value in self.__dict__.items():
                if key not in result and key not in self.__fields__:
                    result[key] = _serialize_value(value)
        return result

    def model_dump(self) -> Dict[str, Any]:
        return self.dict()

    def json(self) -> str:
        return json.dumps(self.dict())

    def model_dump_json(self) -> str:
        return self.json()


def _is_optional(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin is Union:
        return type(None) in get_args(annotation)
    return False


def _validate_type(value: Any, annotation: Any, loc: Tuple[Any, ...], config: Dict[str, Any]) -> Any:
    if annotation is Any or annotation is None:
        return value
    if annotation is type(None):
        if value is None:
            return None
        raise ValidationError([_error(loc, "value is not None", "type_error.none")])
    origin = get_origin(annotation)
    if origin is Union:
        errors: List[Dict[str, Any]] = []
        for arg in get_args(annotation):
            try:
                return _validate_type(value, arg, loc, config)
            except ValidationError as exc:
                errors.extend(exc.errors())
        if not errors:
            errors = [_error(loc, "value does not match any union type", "type_error.union")]
        raise ValidationError(errors)
    if value is None:
        if _is_optional(annotation):
            return None
        raise ValidationError([_error(loc, "none is not an allowed value", "type_error.none.not_allowed")])
    if origin in (list, List, Iterable):
        item_type = get_args(annotation)[0] if get_args(annotation) else Any
        if not isinstance(value, (list, tuple)):
            raise ValidationError([_error(loc, "value is not a valid list", "type_error.list")])
        result = []
        errors: List[Dict[str, Any]] = []
        for idx, item in enumerate(value):
            try:
                result.append(_validate_type(item, item_type, loc + (idx,), config))
            except ValidationError as exc:
                errors.extend(exc.errors())
        if errors:
            raise ValidationError(errors)
        return list(result)
    if origin in (dict, Dict, Mapping):
        key_type, value_type = (get_args(annotation) + (Any, Any))[:2]
        if not isinstance(value, Mapping):
            raise ValidationError([_error(loc, "value is not a valid dict", "type_error.dict")])
        result_dict = {}
        errors: List[Dict[str, Any]] = []
        for key, item in value.items():
            key_loc = loc + (key,)
            try:
                coerced_key = _validate_type(key, key_type, key_loc, config)
            except ValidationError as exc:
                errors.extend(exc.errors())
                continue
            try:
                result_dict[coerced_key] = _validate_type(item, value_type, key_loc, config)
            except ValidationError as exc:
                errors.extend(exc.errors())
        if errors:
            raise ValidationError(errors)
        return result_dict
    if inspect.isclass(annotation):
        if issubclass(annotation, BaseModel):
            try:
                return annotation.parse_obj(value)
            except ValidationError as exc:
                errors = []
                for error in exc.errors():
                    errors.append(_error(loc + tuple(error["loc"]), error["msg"], error["type"]))
                raise ValidationError(errors)
        if annotation in (int, float, str, bool):
            return _coerce_primitive(value, annotation, loc)
        if isinstance(value, annotation):
            return value
        if config.get("arbitrary_types_allowed"):
            return value
        raise ValidationError([_error(loc, f"value is not an instance of {annotation.__name__}", "type_error.arbitrary_type")])
    if annotation in (int, float, str, bool):
        return _coerce_primitive(value, annotation, loc)
    return value


def _coerce_primitive(value: Any, expected_type: Type[Any], loc: Tuple[Any, ...]) -> Any:
    if expected_type is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1"}:
                return True
            if lowered in {"false", "0"}:
                return False
        if isinstance(value, (int, float)):
            if value in {0, 0.0}:
                return False
            if value in {1, 1.0}:
                return True
        raise ValidationError([_error(loc, "value is not a valid boolean", "type_error.bool")])
    if expected_type is int:
        if isinstance(value, bool):
            raise ValidationError([_error(loc, "value is not a valid integer", "type_error.integer")])
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                raise ValidationError([_error(loc, "value is not a valid integer", "type_error.integer")]) from None
        if isinstance(value, float) and value.is_integer():
            return int(value)
        raise ValidationError([_error(loc, "value is not a valid integer", "type_error.integer")])
    if expected_type is float:
        if isinstance(value, bool):
            raise ValidationError([_error(loc, "value is not a valid float", "type_error.float")])
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                raise ValidationError([_error(loc, "value is not a valid float", "type_error.float")]) from None
        raise ValidationError([_error(loc, "value is not a valid float", "type_error.float")])
    if expected_type is str:
        try:
            return str(value)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValidationError([_error(loc, "value is not a valid string", "type_error.string")]) from exc
    raise ValidationError([_error(loc, f"unsupported type {expected_type}", "type_error")])


def _serialize_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.dict()
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(val) for key, val in value.items()}
    return value
