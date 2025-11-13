"""Lightweight subset of Pydantic required by the v10.7 workflow tests."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

__all__ = [
    "BaseModel",
    "ConfigDict",
    "Field",
    "ValidationError",
]


@dataclass
class ConfigDict:
    """Minimal configuration container mirroring the fields we rely on."""

    extra: str = "ignore"
    validate_assignment: bool = False
    arbitrary_types_allowed: bool = True
    populate_by_name: bool = False


class ValidationError(Exception):
    """Structured error that mimics the subset returned by Pydantic."""

    def __init__(self, errors: List[Dict[str, Any]]):
        self._errors = errors
        message = "; ".join(error["msg"] for error in errors)
        super().__init__(message)

    def errors(self) -> List[Dict[str, Any]]:
        return self._errors


class FieldInfo:
    """Stores default metadata for a model field."""

    __slots__ = ("default", "default_factory", "metadata", "required")

    def __init__(
        self,
        *,
        default: Any = ...,
        default_factory: Any | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        self.default = default
        self.default_factory = default_factory
        self.metadata = metadata or {}
        self.required = default is ... and default_factory is None


def Field(
    default: Any = ...,
    *,
    default_factory: Any | None = None,
    **metadata: Any,
) -> FieldInfo:
    if default is not ... and default_factory is not None:
        raise TypeError("cannot specify both default and default_factory")
    return FieldInfo(default=default, default_factory=default_factory, metadata=metadata)


@dataclass
class ModelField:
    name: str
    annotation: Any
    field_info: FieldInfo


class BaseModelMeta(type):
    def __new__(mcls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]):
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__model_fields__ = cls._collect_model_fields()
        return cls


class BaseModel(metaclass=BaseModelMeta):
    """Minimal, deterministic subset of Pydantic's BaseModel."""

    model_config: ConfigDict = ConfigDict()

    @classmethod
    def _collect_model_fields(cls) -> Dict[str, ModelField]:
        fields: Dict[str, ModelField] = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "__model_fields__", {}))
        raw_annotations = getattr(cls, "__annotations__", {})
        try:
            resolved = get_type_hints(cls, include_extras=True)
        except Exception:  # pragma: no cover - defensive fallback
            resolved = raw_annotations
        for name in raw_annotations:
            if name == "model_config":
                continue
            annotation = resolved.get(name, raw_annotations[name])
            origin = get_origin(annotation)
            if origin is ClassVar:
                continue
            field_info = cls._extract_field_info(name)
            fields[name] = ModelField(name=name, annotation=annotation, field_info=field_info)
        return fields

    @classmethod
    def _extract_field_info(cls, name: str) -> FieldInfo:
        attr = getattr(cls, name, ...)
        if isinstance(attr, FieldInfo):
            return attr
        if attr is ...:
            return FieldInfo()
        return FieldInfo(default=attr)

    @classmethod
    def _get_config(cls) -> ConfigDict:
        config = getattr(cls, "model_config", None) or getattr(cls, "__config__", None)
        if isinstance(config, ConfigDict):
            return config
        if isinstance(config, dict):
            return ConfigDict(**config)
        return ConfigDict()

    def __init__(self, **data: Any) -> None:  # noqa: D401 - parity with Pydantic signature
        cls = self.__class__
        config = cls._get_config()
        fields = getattr(cls, "__model_fields__", {})
        provided = dict(data)
        values: Dict[str, Any] = {}
        errors: List[Dict[str, Any]] = []

        for name, model_field in fields.items():
            field_info = model_field.field_info
            if name in provided:
                raw_value = provided.pop(name)
            else:
                if not field_info.required:
                    if field_info.default is not ...:
                        raw_value = field_info.default
                    elif field_info.default_factory is not None:
                        raw_value = field_info.default_factory()
                    else:
                        raw_value = None
                else:
                    errors.append({"loc": [name], "msg": "Field required", "type": "value_error.missing"})
                    continue
            try:
                values[name] = self._coerce_type(
                    model_field.annotation,
                    raw_value,
                    allow_arbitrary=config.arbitrary_types_allowed,
                    loc=[name],
                )
            except ValidationError as field_error:
                errors.extend(field_error.errors())

        extra_behavior = getattr(config, "extra", "ignore")
        if provided and extra_behavior == "forbid":
            for key in provided:
                errors.append({"loc": [key], "msg": "Extra inputs are not permitted", "type": "value_error.extra"})
        elif provided and extra_behavior == "allow":
            values.update(provided)

        if errors:
            raise ValidationError(errors)

        self.__dict__.update(values)

    @classmethod
    def _coerce_type(
        cls,
        annotation: Any,
        value: Any,
        *,
        allow_arbitrary: bool,
        loc: List[Any] | None = None,
    ) -> Any:
        loc_list = list(loc) if loc else []
        origin = get_origin(annotation)
        args = get_args(annotation)

        if annotation in (Any, None) or annotation is object:
            return value

        if annotation is type(None):
            if value is None:
                return None
            raise ValidationError([
                {"loc": loc_list, "msg": "Input should be None", "type": "type_error.none"}
            ])

        if origin is Union:
            return cls._resolve_union(annotation, value, allow_arbitrary=allow_arbitrary, loc=loc)

        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            if isinstance(value, annotation):
                return value
            if isinstance(value, dict):
                try:
                    return annotation(**value)
                except ValidationError as exc:
                    errors = []
                    for nested in exc.errors():
                        nested_loc = list(loc_list) + list(nested.get("loc", []))
                        errors.append(
                            {"loc": nested_loc, "msg": nested["msg"], "type": nested["type"]}
                        )
                    raise ValidationError(errors) from None
            raise ValidationError([
                {"loc": loc_list, "msg": "Input should be a valid dictionary", "type": "type_error.dict"}
            ])

        if origin in (list, List):
            if not isinstance(value, list):
                raise ValidationError([
                    {"loc": loc_list, "msg": "Input should be a valid list", "type": "type_error.list"}
                ])
            item_type = args[0] if args else Any
            return [
                cls._coerce_type(item_type, item, allow_arbitrary=allow_arbitrary, loc=loc_list + [index])
                for index, item in enumerate(value)
            ]

        if origin in (dict, Dict):
            if not isinstance(value, dict):
                raise ValidationError([
                    {"loc": loc_list, "msg": "Input should be a valid dictionary", "type": "type_error.dict"}
                ])
            value_type = args[1] if len(args) > 1 else Any
            return {
                str(key): cls._coerce_type(
                    value_type,
                    item,
                    allow_arbitrary=allow_arbitrary,
                    loc=loc_list + [str(key)],
                )
                for key, item in value.items()
            }

        if annotation is int:
            if isinstance(value, bool):
                raise ValidationError([
                    {"loc": loc_list, "msg": "Input should be a valid integer", "type": "type_error.integer"}
                ])
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                try:
                    return int(value.strip())
                except ValueError:
                    pass
            if isinstance(value, float) and value.is_integer():
                return int(value)
            raise ValidationError([
                {"loc": loc_list, "msg": "Input should be a valid integer", "type": "type_error.integer"}
            ])

        if annotation is float:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value.strip())
                except ValueError:
                    pass
            raise ValidationError([
                {"loc": loc_list, "msg": "Input should be a valid float", "type": "type_error.float"}
            ])

        if annotation is bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"true", "1"}:
                    return True
                if lowered in {"false", "0"}:
                    return False
            if isinstance(value, (int, float)):
                if value in {0, 1}:
                    return bool(value)
            raise ValidationError([
                {"loc": loc_list, "msg": "Input should be a valid boolean", "type": "type_error.bool"}
            ])

        if annotation is str:
            if isinstance(value, str):
                return value
            return str(value)

        if allow_arbitrary and isinstance(annotation, type):
            if isinstance(value, annotation):
                return value
            try:
                return annotation(value)
            except Exception as exc:  # pragma: no cover - mirrors Pydantic messaging
                raise ValidationError([
                    {"loc": loc_list, "msg": str(exc), "type": "type_error.arbitrary_type"}
                ]) from None

        return value

    @classmethod
    def _resolve_union(
        cls,
        annotation: Any,
        value: Any,
        *,
        allow_arbitrary: bool,
        loc: List[Any] | None = None,
    ) -> Any:
        args = get_args(annotation)
        loc_list = list(loc) if loc else []

        for candidate in args:
            if candidate is type(None) and value is None:
                return None
            if isinstance(candidate, type) and isinstance(value, candidate):
                return cls._coerce_type(candidate, value, allow_arbitrary=allow_arbitrary, loc=loc_list)

        for candidate in args:
            try:
                return cls._coerce_type(candidate, value, allow_arbitrary=allow_arbitrary, loc=loc_list)
            except ValidationError:
                continue

        raise ValidationError([
            {"loc": loc_list, "msg": "Input should match at least one type", "type": "type_error.union"}
        ])

    def dict(self) -> Dict[str, Any]:
        return {key: self._export(value) for key, value in self.__dict__.items() if not key.startswith("_")}

    def model_dump(self) -> Dict[str, Any]:
        return self.dict()

    def json(self) -> str:
        return self.model_dump_json()

    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump())

    def model_copy(self, *, deep: bool = False) -> "BaseModel":
        data = self.model_dump()
        if deep:
            data = deepcopy(data)
        return self.__class__(**data)

    @classmethod
    def parse_obj(cls, obj: Any) -> "BaseModel":
        return cls.model_validate(obj)

    @classmethod
    def model_validate(cls, data: Any) -> "BaseModel":
        if isinstance(data, cls):
            return data
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as exc:
                raise ValidationError([
                    {"loc": ["__root__"], "msg": f"JSON decode error: {exc.msg}", "type": "value_error.json"}
                ]) from None
        if not isinstance(data, dict):
            raise ValidationError([
                {"loc": ["__root__"], "msg": "Input should be a valid dictionary", "type": "type_error.dict"}
            ])
        return cls(**data)

    @staticmethod
    def _export(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump()
        if isinstance(value, list):
            return [BaseModel._export(item) for item in value]
        if isinstance(value, dict):
            return {key: BaseModel._export(item) for key, item in value.items()}
        return value
