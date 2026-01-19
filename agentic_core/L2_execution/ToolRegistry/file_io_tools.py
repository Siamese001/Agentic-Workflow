from __future__ import annotations
"""
File I/O Tools - Atomic Module
Extracted from action_registry.py via Atomic Fission Protocol
Tool ID Prefix: ACT-002
"""
import logging
import os
from typing import Any, Dict, List, Optional, Protocol
try:
    import PyPDF2
except ImportError:
    PyPDF2: Any = None
Logger: Any = logging.getLogger('ActionRegistry.FileIO')

class FileIo:
    """
    Handles file reading and saving operations.
    Tool ID Prefix: ACT-002
    """

    def __init__(self):
        """Initializes FileIO. No specific state needed for file operations."""

    def _read_pdf_file(self, file_path: str) -> str:
        """
        Helper to read content from a PDF file.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            str: The extracted text content from the PDF.
        """
        if not PyPDF2:
            return 'Error: PyPDF2 module not installed. Cannot read PDF files.'
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return self._extract_pdf_pages_text(reader, file_path)
        except PyPDF2.errors.PdfReadError as e:
            return f"Read Error (PDF): Could not read PDF file '{file_path}'. {e}"
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."
        except Exception as e:
            return f'Read Error (PDF Unexpected): {e}'

    def _extract_pdf_pages_text(self, reader, file_path: str) -> str:
        """
        Extracts text content from PDF reader pages.

        Args:
            reader: The PyPDF2.PdfReader object.
            file_path (str): The path to the PDF file (for error messages).

        Returns:
            str: The extracted text content from the PDF or a warning message.
        """
        if not reader.pages:
            return f"Warning: PDF file '{file_path}' has no pages or content."
        extracted_texts = [page.extract_text() for page in reader.pages if page.extract_text()]
        return '\n'.join(extracted_texts)

    def _read_text_file(self, file_path: str) -> str:
        """
        Helper to read content from a text-based file.

        Args:
            file_path (str): The path to the text file.

        Returns:
            str: The content of the text file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."
        except UnicodeDecodeError:
            return f"Read Error: Could not decode file '{file_path}' with utf-8. Try a different encoding."
        except Exception as e:
            return f'Read Error (Text Unexpected): {e}'

    def read_file(self, file_path: str) -> str:
        """
        Reads text content from agentic_core.txt, .md, or .pdf files.
        Tool ID: ACT-002

        Args:
            file_path (str): The path to the file to read.

        Returns:
            str: The content of the file or an error message.
        """
        Logger.info(f"📖 Reading file: '{file_path}'")
        if not os.path.exists(file_path):
            return f"Read Error: File not found at '{file_path}'."
        if file_path.endswith('.pdf'):
            return self._read_pdf_file(file_path)
        else:
            return self._read_text_file(file_path)

    def save_file(self, content: str, file_path: str) -> str:
        """
        Saves content to a file.
        Tool ID: ACT-003

        Args:
            content (str): The string content to save.
            file_path (str): The path where the file should be saved.

        Returns:
            str: A success message or an error message.
        """
        Logger.info(f"[SAVE] Saving file: '{file_path}' (content length: {len(content)})")
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f'[OK] File saved successfully: {file_path}'
        except IOError as e:
            return f"Save Error (IO): Could not save file '{file_path}'. {e}"
        except Exception as e:
            return f'Save Error (Unexpected): {e}'
__all__ = ['FileIO']
