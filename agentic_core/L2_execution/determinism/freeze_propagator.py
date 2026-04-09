"""C1.2: Replay Mode Propagation - Freeze signal across layers.

10C-REQ-118: Inject Freeze signal across layers L0->L3->L5->L2
halt wall-clock updates ensure same snapshot seen by all
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable


class FreezeState(Enum):
    """Freeze state enumeration."""
    UNFROZEN = auto()
    FREEZING = auto()
    FROZEN = auto()
    THAWING = auto()


@dataclass
class FreezeSignal:
    """Freeze signal for layer propagation."""
    source_layer: str
    target_layers: list[str]
    freeze_state: FreezeState
    timestamp: float
    replay_key: str = ""
    snapshot_id: str = ""


class FreezePropagator:
    """Propagates freeze signals across layers.
    
    10C-REQ-118: Propagate replay mode inject Freeze signal across
    L0->L3->L5->L2 halt wall-clock updates ensure same snapshot.
    """
    
    LAYER_ORDER = ["L0", "L3", "L5", "L2"]
    
    def __init__(self) -> None:
        self._layer_states: dict[str, FreezeState] = {
            layer: FreezeState.UNFROZEN for layer in self.LAYER_ORDER
        }
        self._handlers: dict[str, list[Callable[[FreezeSignal], None]]] = {
            layer: [] for layer in self.LAYER_ORDER
        }
        self._lock: threading.Lock = threading.Lock()
        self._wall_clock_halted: bool = False
        self._frozen_timestamp: float | None = None
    
    def propagate_freeze(self, source: str, replay_key: str, snapshot_id: str) -> bool:
        """Propagate freeze signal from source through all layers.
        
        Returns True if all layers successfully frozen.
        """
        with self._lock:
            # Start from source layer
            try:
                start_idx = self.LAYER_ORDER.index(source)
            except ValueError:
                return False
            
            # Halt wall clock
            self._wall_clock_halted = True
            self._frozen_timestamp = time.time()
            
            # Propagate through remaining layers in order
            signal = FreezeSignal(
                source_layer=source,
                target_layers=self.LAYER_ORDER[start_idx:],
                freeze_state=FreezeState.FREEZING,
                timestamp=self._frozen_timestamp,
                replay_key=replay_key,
                snapshot_id=snapshot_id,
            )
            
            for layer in self.LAYER_ORDER[start_idx:]:
                self._layer_states[layer] = FreezeState.FREEZING
                # Notify handlers
                for handler in self._handlers[layer]:
                    handler(signal)
                self._layer_states[layer] = FreezeState.FROZEN
            
            return all(
                state == FreezeState.FROZEN
                for state in self._layer_states.values()
            )
    
    def thaw(self, source: str) -> bool:
        """Thaw (unfreeze) all layers."""
        with self._lock:
            signal = FreezeSignal(
                source_layer=source,
                target_layers=self.LAYER_ORDER,
                freeze_state=FreezeState.THAWING,
                timestamp=time.time(),
            )
            
            for layer in self.LAYER_ORDER:
                self._layer_states[layer] = FreezeState.THAWING
                for handler in self._handlers[layer]:
                    handler(signal)
                self._layer_states[layer] = FreezeState.UNFROZEN
            
            self._wall_clock_halted = False
            self._frozen_timestamp = None
            return True
    
    def register_handler(self, layer: str, handler: Callable[[FreezeSignal], None]) -> None:
        """Register a freeze handler for a layer."""
        if layer in self._handlers:
            self._handlers[layer].append(handler)
    
    def is_frozen(self, layer: str | None = None) -> bool:
        """Check if frozen (globally or for specific layer)."""
        with self._lock:
            if layer is None:
                return any(
                    state == FreezeState.FROZEN
                    for state in self._layer_states.values()
                )
            return self._layer_states.get(layer) == FreezeState.FROZEN
    
    def get_frozen_timestamp(self) -> float | None:
        """Get the frozen timestamp (deterministic clock)."""
        return self._frozen_timestamp
    
    def wall_clock_halted(self) -> bool:
        """Check if wall clock is halted."""
        return self._wall_clock_halted
