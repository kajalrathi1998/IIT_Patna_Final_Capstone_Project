import streamlit as st
from pathlib import Path
import sys

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


# Create directories if they don't exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Complaint Processing",
    page_icon="📄",
    layout="centered"
)


st.title("📄 Complaint Processing Pipeline")


# --------------------------------------------------
# File Upload
# --------------------------------------------------

st.header("1. Upload Files")

uploaded_files = st.file_uploader(
    "Select complaint files",
    accept_multiple_files=True
)


if uploaded_files:

    for uploaded_file in uploaded_files:

        file_path = INPUT_DIR / uploaded_file.name

        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

    st.success(
        f"{len(uploaded_files)} file(s) uploaded successfully."
    )


# Show files currently available
input_files = [
    file for file in INPUT_DIR.iterdir()
    if file.is_file()
]

st.write(f"Files available in input folder: **{len(input_files)}**")


# --------------------------------------------------
# Number of files
# --------------------------------------------------

st.header("2. Run Pipeline")

number_of_files = st.number_input(
    "Number of files to process",
    min_value=1,
    max_value=max(1, len(input_files)),
    value=min(1, max(1, len(input_files))),
    step=1
)


# --------------------------------------------------
# Start Pipeline
# --------------------------------------------------

if st.button("▶️ Start Processing", type="primary"):

    if len(input_files) == 0:

        st.error("Please upload at least one file.")

    else:

        batch_size = int(number_of_files)
        total_files = len(input_files)

        progress_bar = st.progress(0)
        status_text = st.empty()

        processed_files = 0
        batch_number = 1

        try:

            import main

            while processed_files < total_files:

                # Files remaining to process
                remaining_files = total_files - processed_files

                # Number of files for this batch
                current_batch_size = min(
                    batch_size,
                    remaining_files
                )

                status_text.write(
                    f"Processing batch {batch_number} "
                    f"({current_batch_size} files)..."
                )

                # Run pipeline
                main.main(current_batch_size)

                # Update count
                processed_files += current_batch_size

                # Update progress
                progress = processed_files / total_files
                progress_bar.progress(progress)

                status_text.write(
                    f"Completed {processed_files} "
                    f"of {total_files} files."
                )

                batch_number += 1

            st.success(
                f"All {total_files} files processed successfully! ✅"
            )

        except Exception as e:

            st.error(
                f"Pipeline failed after processing "
                f"{processed_files} files: {e}"
            )


# --------------------------------------------------
# Download Output CSV Files
# --------------------------------------------------

st.header("3. Download Output Files")


output_files = list(OUTPUT_DIR.glob("*.csv"))


if not output_files:

    st.info(
        "No output CSV files available yet."
    )

else:

    for output_file in output_files:

        with open(output_file, "rb") as file:

            st.download_button(
                label=f"⬇️ {output_file.name}",
                data=file,
                file_name=output_file.name,
                mime="text/csv"
            )