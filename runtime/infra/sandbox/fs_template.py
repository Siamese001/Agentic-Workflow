# Filesystem template for sandbox isolation
from typing import Dict, Any, List

def build_ephemeral_rootfs() -> Dict[str, Any]:
    """Build an ephemeral root filesystem for sandbox isolation"""
    return {
        "tmpfs": True,
        "restricted_paths": ["/", "/etc", "/usr", "/bin", "/sbin"],
        "writable_paths": ["/tmp", "/var/tmp", "/home"],
        "read_only_paths": ["/etc/passwd", "/etc/group"],
        "mount_options": {
            "tmpfs_size": "100M",
            "noexec": True,
            "nosuid": True,
            "nodev": True
        }
    }
