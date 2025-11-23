from __future__ import annotations

from typing import Dict, List


def build_ephemeral_rootfs() -> Dict[str, object]:
    """Return a deterministic description of an ephemeral rootfs.

    This does not perform any real filesystem mutation; instead it
    returns a structure that can be inspected in tests.
    """

    return {
        "tmpfs": True,
        "restricted_paths": ["/", "/etc", "/var", "/home"],
        "writable_paths": ["/tmp", "/sandbox"],
    }
