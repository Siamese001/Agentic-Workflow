from infra.sandbox.fs_template import build_ephemeral_rootfs


def test_build_ephemeral_rootfs_shape():
    fs = build_ephemeral_rootfs()

    assert fs.get("tmpfs") is True
    assert "/" in fs.get("restricted_paths", [])
    assert "/tmp" in fs.get("writable_paths", [])
