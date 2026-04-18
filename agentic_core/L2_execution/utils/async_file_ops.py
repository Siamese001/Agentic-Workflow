"""Async File Operations - Wave 3 CPU Optimization.

Provides asynchronous file I/O to eliminate I/O bottlenecks
and allow CPU to work on other tasks during file operations.
"""

from __future__ import annotations

import asyncio
import logging
import mmap
from dataclasses import dataclass
from typing import Any

import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class FileReadResult:
    """Result from async file read."""

    file_path: str
    content: bytes | str
    size: int
    read_time_ms: float
    success: bool = True
    error: str | None = None


class AsyncFileProcessor:
    """Asynchronous file processor for non-blocking I/O.

    Uses aiofiles for async file operations, allowing CPU to
    continue working while waiting for I/O completion.
    """

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def read_file_async(
        self,
        file_path: str,
        mode: str = "r",
        encoding: str = "utf-8",
    ) -> FileReadResult:
        """Read file asynchronously.

        Args:
            file_path: Path to file
            mode: 'r' for text, 'rb' for binary
            encoding: Text encoding (for text mode)

        Returns:
            FileReadResult with content or error
        """
        import time

        start = time.time()

        try:
            async with self._semaphore:
                if mode == "rb":
                    async with aiofiles.open(file_path, "rb") as f:
                        content = await f.read()
                else:
                    async with aiofiles.open(file_path, encoding=encoding) as f:
                        content = await f.read()

                elapsed_ms = (time.time() - start) * 1000

                return FileReadResult(
                    file_path=file_path,
                    content=content,
                    size=len(content) if isinstance(content, (bytes, str)) else 0,
                    read_time_ms=elapsed_ms,
                    success=True,
                )

        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            elapsed_ms = (time.time() - start) * 1000
            return FileReadResult(
                file_path=file_path,
                content=b"" if mode == "rb" else "",
                size=0,
                read_time_ms=elapsed_ms,
                success=False,
                error=str(e),
            )

    async def read_json_async(self, file_path: str) -> Any:
        """Read and parse JSON file asynchronously."""
        import json

        result = await self.read_file_async(file_path, mode="r")

        if not result.success:
            raise ValueError(f"Failed to read {file_path}: {result.error}")

        return json.loads(result.content)

    async def read_multiple(
        self,
        file_paths: list[str],
        mode: str = "r",
    ) -> list[FileReadResult]:
        """Read multiple files concurrently.

        Args:
            file_paths: List of file paths
            mode: Read mode ('r' or 'rb')

        Returns:
            List of FileReadResult objects
        """
        tasks = [self.read_file_async(path, mode) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)


class MemoryMappedFileReader:
    """Memory-mapped file reader for large files.

    Uses mmap for efficient access to large files without
    loading entire content into memory.
    """

    def __init__(self, buffer_size: int = 8192):
        self.buffer_size = buffer_size

    def read_mmap(
        self,
        file_path: str,
        offset: int = 0,
        size: int | None = None,
    ) -> bytes:
        """Read file using memory mapping.

        Args:
            file_path: Path to file
            offset: Starting offset
            size: Number of bytes to read (None = all)

        Returns:
            File content as bytes
        """
        with open(file_path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                if size is None:
                    return mm[offset:]
                else:
                    return mm[offset : offset + size]

    def read_lines_mmap(self, file_path: str) -> list[bytes]:
        """Read file line by line using memory mapping.

        Efficient for large text files - avoids loading
        entire file into memory.
        """
        lines = []

        with open(file_path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Iterate over lines in memory-mapped file
                for line in mm.read().split(b"\n"):
                    if line:
                        lines.append(line)

        return lines

    def search_in_file(
        self,
        file_path: str,
        pattern: bytes,
    ) -> list[int]:
        """Search for pattern in file using memory mapping.

        Returns list of offsets where pattern is found.
        """
        offsets = []

        with open(file_path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                offset = mm.find(pattern)
                while offset != -1:
                    offsets.append(offset)
                    offset = mm.find(pattern, offset + 1)

        return offsets


class BufferedFileWriter:
    """Buffered file writer for optimized write operations.

    Buffers writes to reduce system calls and improve throughput.
    """

    def __init__(self, buffer_size: int = 65536):  # 64KB default
        self.buffer_size = buffer_size

    def write_buffered(
        self,
        file_path: str,
        content_generator,
        mode: str = "w",
        encoding: str = "utf-8",
    ) -> int:
        """Write content with buffering.

        Args:
            file_path: Output file path
            content_generator: Generator yielding content chunks
            mode: 'w' for text, 'wb' for binary
            encoding: Text encoding

        Returns:
            Total bytes written
        """
        total_written = 0

        if "b" in mode:
            with open(file_path, mode, buffering=self.buffer_size) as f:
                for chunk in content_generator:
                    if isinstance(chunk, str):
                        chunk = chunk.encode(encoding)
                    f.write(chunk)
                    total_written += len(chunk)
        else:
            with open(file_path, mode, buffering=self.buffer_size, encoding=encoding) as f:
                for chunk in content_generator:
                    f.write(chunk)
                    total_written += len(chunk)

        return total_written

    def write_json_lines(
        self,
        file_path: str,
        records: list[dict],
        batch_size: int = 100,
    ) -> int:
        """Write JSON Lines format (one JSON object per line).

        Efficient for large datasets - processes in batches.
        """
        import json

        total = 0

        with open(file_path, "w", buffering=self.buffer_size) as f:
            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                lines = [json.dumps(r) + "\n" for r in batch]
                f.writelines(lines)
                total += len(batch)

        return total


class StreamingFileProcessor:
    """Streaming processor for very large files.

    Processes files in chunks without loading into memory.
    """

    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size

    def process_streaming(
        self,
        file_path: str,
        processor_func,
        mode: str = "rb",
    ):
        """Process file in streaming fashion.

        Args:
            file_path: Input file path
            processor_func: Function to process each chunk
            mode: File open mode

        Yields:
            Processed results from each chunk
        """
        with open(file_path, mode) as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break

                result = processor_func(chunk)
                if result is not None:
                    yield result

    async def process_streaming_async(
        self,
        file_path: str,
        processor_func,
        mode: str = "rb",
    ):
        """Async streaming file processor."""
        async with aiofiles.open(file_path, mode) as f:
            while True:
                chunk = await f.read(self.chunk_size)
                if not chunk:
                    break

                result = processor_func(chunk)
                if result is not None:
                    yield result


# Singleton instances
_async_processor: AsyncFileProcessor | None = None
_mmap_reader: MemoryMappedFileReader | None = None


def get_async_processor(max_concurrent: int = 10) -> AsyncFileProcessor:
    """Get singleton async file processor."""
    global _async_processor
    if _async_processor is None:
        _async_processor = AsyncFileProcessor(max_concurrent)
    return _async_processor


def get_mmap_reader(buffer_size: int = 8192) -> MemoryMappedFileReader:
    """Get singleton memory-mapped file reader."""
    global _mmap_reader
    if _mmap_reader is None:
        _mmap_reader = MemoryMappedFileReader(buffer_size)
    return _mmap_reader


__all__ = [
    "AsyncFileProcessor",
    "MemoryMappedFileReader",
    "BufferedFileWriter",
    "StreamingFileProcessor",
    "FileReadResult",
    "get_async_processor",
    "get_mmap_reader",
]
