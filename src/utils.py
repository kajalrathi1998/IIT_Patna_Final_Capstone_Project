from pathlib import Path
from typing import List
import pandas as pd
# ============================================================
# File Discovery
# ============================================================

def discover_files(input_dir: Path, patterns: List = ["*.pdf", "*.txt","*.docx"], number_of_files=None) -> pd.DataFrame:
    """
    Discovers files inside a provided path and returns
    a standardized DataFrame.

    Arguments:
        input_dir (Path)
        pattern (str)

    Returns:
        pd.DataFrame
    """
    if number_of_files:
        files = sorted(
            file
            for pattern in patterns
            for file in input_dir.glob(pattern)
        )[:number_of_files]
    else:
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
            "parse_status": "Pending",
        }
    )

def load_prompt(prompt_path: Path) -> str:
    """
    Loads a prompt from a text file.

    Args:
        prompt_path (Path): Prompt file path.

    Returns:
        str
    """
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

# def save_dataframe(
#     dataframe: pd.DataFrame,
#     output_path: Path,
# ):
#     """
#     Saves a DataFrame to CSV.
#     """

#     output_path.parent.mkdir(
#         parents=True,
#         exist_ok=True,
#     )

#     dataframe.to_csv(
#         output_path,
#         index=False,
#     )

def save_dataframe(
    dataframe: pd.DataFrame,
    output_path: Path,
):
    """
    Saves a DataFrame to CSV.
    Appends to the existing file if it already exists.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Append if file already exists
    if output_path.exists():
        dataframe.to_csv(
            output_path,
            mode="a",
            header=False,
            index=False,
        )
    else:
        dataframe.to_csv(
            output_path,
            mode="w",
            header=True,
            index=False,
        )