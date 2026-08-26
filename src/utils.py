from pathlib import Path
from typing import List
import pandas as pd
# ============================================================
# File Discovery
# ============================================================

def discover_files(input_dir: Path, patterns: List = ["*.pdf", "*.txt","*.docs"]) -> pd.DataFrame:
    """
    Discovers files inside a provided path and returns
    a standardized DataFrame.

    Arguments:
        input_dir (Path)
        pattern (str)

    Returns:
        pd.DataFrame
    """

    files = sorted(
        file
        for pattern in patterns
        for file in input_dir.glob(pattern)
    )

    if not files:
        raise FileNotFoundError(
            f"No files found in: {input_dir}"
        )

    return pd.DataFrame(
        {
            "file_name": [file.name for file in files],
            "file_path": [str(file) for file in files],
            "file_size_kb": [
                round(file.stat().st_size / 1024, 2)
                for file in files
            ],
            "status": "Pending",
        }
    )
