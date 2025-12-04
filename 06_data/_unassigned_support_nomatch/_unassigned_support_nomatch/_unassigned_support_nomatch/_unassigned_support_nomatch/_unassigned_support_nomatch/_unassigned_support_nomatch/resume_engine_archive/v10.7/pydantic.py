class ValidationError(Exception):
    pass


def Field(default=..., *, default_factory=None, **_kwargs):  # pragma: no cover - stub
    if default is ... and default_factory is not None:
        return default_factory()
    return default


class BaseModel:
    """Minimal stand-in for pydantic.BaseModel used in tests."""

    def __init__(self, **data):
        annotations = getattr(self, "__annotations__", {})
        for name, annotation in annotations.items():
            if name in data:
                value = data[name]
            elif hasattr(self, name):
                value = getattr(self, name)
                if value is ...:
                    raise ValidationError(f"Field '{name}' is required")
            else:
                raise ValidationError(f"Field '{name}' is required")
            setattr(self, name, value)

        for extra_key, extra_value in data.items():
            if extra_key not in annotations:
                setattr(self, extra_key, extra_value)

    def dict(self):
        annotations = getattr(self, "__annotations__", {})
        return {name: getattr(self, name) for name in annotations}

    def model_dump(self):
        return self.dict()

    @classmethod
    def model_validate(cls, data):
        if isinstance(data, cls):
            return data
        if isinstance(data, dict):
            return cls(**data)
        raise ValidationError(f"Cannot validate data for {cls.__name__}: {data!r}")
