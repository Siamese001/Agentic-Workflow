"""
L5 D0 Injection Engine - Deterministic Role Fence Rendering

Implements deterministic D0 injection with RoleFence ordering and rendering.
No wall-clock usage, no randomness, pure deterministic behavior.
"""
from dataclasses import dataclass
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass(frozen=True)
class RoleFence:
    """Immutable role fence for D0 injection."""
    fence_id: str
    text: str

class D0InjectionEngine:
    """
    Deterministic D0 injection engine for role fences.

    Renders fences in deterministic order with no mutation of input objects.
    """

    def render_d0(self, *, fences: tuple[RoleFence, ...]) -> str:
        """
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
        """
        sorted_fences = sorted(fences, key=lambda f: f.fence_id)
        lines = ['<D0>']
        for fence in sorted_fences:
            lines.append(f'[{fence.fence_id}] {fence.text}')
        lines.append('</D0>')
        return '\n'.join(lines) + '\n'

    def inject(self, *, payload_like: object, fences: tuple[RoleFence, ...]) -> str:
        """
        Inject D0 fences into payload context.

        Returns the computed D0 string only.
        Does NOT mutate payload_like.
        Does NOT import or depend on L0 types.

        Args:
            payload_like: Object to inject into (not modified)
            fences: Tuple of RoleFence objects

        Returns:
            Rendered D0 string
        """
        return self.render_d0(fences=fences)
