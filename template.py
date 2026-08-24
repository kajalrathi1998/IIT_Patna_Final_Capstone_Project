"""
template.py

Run:
    python template.py

This script creates the initial project structure for the
AI-Powered Document Processing & Business Workflow project.

Project:
    AI Customer Complaint & Case Processing System
"""

from pathlib import Path


# ==========================
# Files to Create
# ==========================
FILES = [

    # --------------------------
    # Root Files
    # --------------------------
    ".env",
    "README.md",
    "requirements.txt",
    "config.toml",
    "main.py"

    # --------------------------
    # Notebooks
    # --------------------------
    "notebooks/document_processing_pipeline.ipynb",

    # --------------------------
    # Source
    # --------------------------
    "src/__init__.py",
    "src/config.py",
    "src/logger.py",

    # Document Processing
    "src/document_ingestion.py",
    "src/document_processor.py",

    # LLM / AI
    "src/llm_manager.py",

    # Utilities
    "src/utils.py",

    # --------------------------
    # Schemas
    # --------------------------
    "src/schemas/__init__.py",
    "src/schemas/complaint_schema.py",
    "src/schemas/email_schema.py",
    "src/schemas/case_summary_schema.py",

    # --------------------------
    # Prompts
    # --------------------------
    "prompts/complaint_extraction_prompt.txt",
    "prompts/customer_email_prompt.txt",
    "prompts/case_summary_prompt.txt",
]


# ==========================
# Directories to Create
# ==========================
DIRECTORIES = [

    # Input documents
    "data/input",

    # Optional sample documents
    "data/sample_data",

    # Output
    "data/output/structured_data",
    "data/output/customer_emails",
    "data/output/case_summaries",

    # Logs
    "logs",
]


def create_project_structure():
    """
    Create the complete project directory structure.
    """

    # Current directory where template.py is located
    root = Path(__file__).parent.resolve()

    # ==========================
    # Create Directories
    # ==========================
    for directory in DIRECTORIES:
        dir_path = root / directory
        dir_path.mkdir(parents=True, exist_ok=True)

    # ==========================
    # Create Files
    # ==========================
    for file in FILES:

        file_path = root / file

        # Make sure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Don't overwrite existing files
        if not file_path.exists():

            # Create empty notebook
            if file_path.suffix == ".ipynb":
                file_path.write_text("{}", encoding="utf-8")

            else:
                file_path.touch()

    # ==========================
    # Success Message
    # ==========================
    print("=" * 60)
    print("Project structure created successfully!")
    print(f"Location: {root}")
    print("=" * 60)


if __name__ == "__main__":
    create_project_structure()