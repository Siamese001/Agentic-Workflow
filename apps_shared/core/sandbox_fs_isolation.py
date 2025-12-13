# from archives.legacy_root_folders.infra.sandbox.fs_template import build_ephemeral_rootfs  # DEPRECATED: Archive import removed to protect archives from validation edits

def test_build_ephemeral_rootfs_shape() -> None:
    fs = build_ephemeral_rootfs()

    assert fs.get("tmpfs") is True
    assert "/" in fs.get("restricted_paths", [])
    assert "/tmp" in fs.get("writable_paths", [])
