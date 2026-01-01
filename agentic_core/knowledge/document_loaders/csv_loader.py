import pandas as pd
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import List, Dict, Any

class CsvDocumentLoader:
    """Sovereign CSV loader using pandas for structured data."""

    @staticmethod
    def load(file_path: Path, **kwargs) -> List[Dict[str, Any]]:
        """
        Load CSV as list of dictionaries (records).

        Supports:
        - Automatic type inference
        - Custom delimiter, encoding
        - Header row handling

        Args:
            file_path: Path to CSV
            kwargs: Passed to pd.read_csv (e.g., delimiter=";", encoding="utf-8")

        Returns:
            List of row dictionaries
        """
        try:
            df: Any = pd.read_csv(file_path, **kwargs)
            records: Any = df.to_dict(orient='records')
            return records
        except Exception as e:
            raise ValueError(f'CSV loading failed for {file_path}: {e}')

    @staticmethod
    def load_as_dataframe(file_path: Path, **kwargs) -> pd.DataFrame:
        """Load as pandas DataFrame for advanced processing."""
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            raise ValueError(f'CSV DataFrame load failed: {e}')

    @staticmethod
    def load_sample(file_path: Path, rows: int=10, **kwargs) -> List[Dict[str, Any]]:
        """Load only first N rows for preview/sampling."""
        try:
            df: Any = pd.read_csv(file_path, nrows=rows, **kwargs)
            return df.to_dict(orient='records')
        except Exception as e:
            raise ValueError(f'CSV sample load failed: {e}')
