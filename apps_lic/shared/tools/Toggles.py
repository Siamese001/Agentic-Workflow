"""Reasoning toggles for the LIC outreach stack."""


class ReasoningToggles(BaseModel):
    """Bounded reasoning configuration shared across the stack."""

    cot: bool = True
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 3
    reflexion: bool = True
    temperature_cap: float = 0.5

    def __init__(self, **data):
        super().__init__(**data)
        self._enforce_bounds()

    def _enforce_bounds(self) -> None:
        if not 1 <= int(self.tot_branches) <= 4:
            raise ValidationError("tot_branches must be between 1 and 4")
        if not 1 <= int(self.min_tot_depth) <= 3:
            raise ValidationError("min_tot_depth must be between 1 and 3")
        if not 1 <= int(self.self_consistency) <= 5:
            raise ValidationError("self_consistency must be between 1 and 5")
        if not 0.1 <= float(self.temperature_cap) <= 0.9:
            raise ValidationError("temperature_cap must be between 0.1 and 0.9")
