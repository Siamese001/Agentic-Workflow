"""Filesystem MCP client for L0 routing providers."""

from __future__ import annotations

from pathlib import Path


class FilesystemMCPClient:
    """Client for filesystem operations via MCP."""

    def __init__(self) -> None:
        self._base_path: Path | None = None

    def set_base_path(self, path: str | Path) -> None:
        """Set the base path for filesystem operations."""
        self._base_path = Path(path)

    async def read_text(self, file_path: str | Path) -> str | None:
        """Read text from a file."""
        try:
            path = Path(file_path)
            if self._base_path:
                path = self._base_path / path
            if not path.exists():
                return None
            return path.read_text(encoding="utf-8")
        except (
            OSError,
            UnicodeDecodeError,
        ) as e:  # guardian: allow-silent-swallow -- file read failure returns None
            return None

    async def write_text(self, file_path: str | Path, content: str) -> bool:
        """Write text to a file."""
        try:
            path = Path(file_path)
            if self._base_path:
                path = self._base_path / path
            path.write_text(content, encoding="utf-8")
            return True
        except (
            OSError,
            PermissionError,
        ) as e:  # guardian: allow-silent-swallow -- file write failure returns False
            return False

    async def list_files(self, directory: str | Path | None = None) -> list[str]:
        """List files in a directory."""
        try:
            path = Path(directory) if directory else self._base_path
            if not path or not path.exists():
                return []
            return [str(f) for f in path.iterdir() if f.is_file()]
        except (
            OSError,
            PermissionError,
        ) as e:  # guardian: allow-silent-swallow -- directory list failure returns empty
            return []


class FilesystemMCPClientFactory:
    """Factory for creating filesystem MCP clients."""

    _instances: dict[str, FilesystemMCPClient] = {}

    @classmethod
    def get_client(cls, name: str = "default") -> FilesystemMCPClient:
        """Get or create a filesystem MCP client."""
        if name not in cls._instances:
            cls._instances[name] = FilesystemMCPClient()
        return cls._instances[name]

    @classmethod
    def reset_client(cls, name: str = "default") -> None:
        """Reset a client instance."""
        if name in cls._instances:
            del cls._instances[name]


def get_filesystem_client(name: str = "default") -> FilesystemMCPClient:
    """Get a filesystem MCP client instance."""
    return FilesystemMCPClientFactory.get_client(name)


__all__ = [
    "FilesystemMCPClient",
    "FilesystemMCPClientFactory",
    "get_filesystem_client",
]
