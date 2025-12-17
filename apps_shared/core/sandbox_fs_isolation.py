import logging

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


def test_build_ephemeral_rootfs_shape() -> None:
    """TODO: Add docstring."""
    build_ephemeral_rootfs()
    assert ConfigurationService().fs.get('tmpfs') is True
    assert '/' in ConfigurationService().fs.get('restricted_paths', [])
    assert '/tmp' in ConfigurationService().fs.get('writable_paths', [])

