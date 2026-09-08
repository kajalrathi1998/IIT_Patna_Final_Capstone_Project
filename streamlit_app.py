import streamlit as st
from pathlib import Path
import sys

from src.config import config

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_DIR = PROJECT_ROOT / config.PATHS['document_input']
OUTPUT_DIR = PROJECT_ROOT / config.PATHS['final_output']
STRUCTURED_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['structured_data_dir']
EMAIL_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['email_data_dir']
SUMMARY_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['summary_data_dir']

# Create directories if they don't exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STRUCTURED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EMAIL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Complaint Processing",
    page_icon="📄",
    layout="centered"
)


st.title("📄 Complaint Processing Pipeline")


# File Upload
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


# Number of files
st.header("2. Run Pipeline")

number_of_files = st.number_input(
    "Batch size for files to process",
    min_value=1,
    max_value=max(1, len(input_files)),
    value=min(1, max(1, len(input_files))),
    step=1
)


# Start Pipeline
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


# Download Output CSV Files
st.header("3. Download Output Files")


final_report_files = list(OUTPUT_DIR.glob("*.csv"))

if not final_report_files:

    st.info(
        "Final report CSV file is not available yet."
    )

else:

    for output_file in final_report_files:

        with open(output_file, "rb") as file:

            st.download_button(
                label=f"⬇️ {output_file.name}",
                data=file,
                file_name=output_file.name,
                mime="text/csv"
            )

complaint_files = list(STRUCTURED_OUTPUT_DIR.glob("*.csv"))

if not complaint_files:

    st.info(
        "Complaints CSV file is not available yet."
    )

else:

    for output_file in complaint_files:

        with open(output_file, "rb") as file:

            st.download_button(
                label=f"⬇️ {output_file.name}",
                data=file,
                file_name=output_file.name,
                mime="text/csv"
            )

customer_email_files = list(EMAIL_OUTPUT_DIR.glob("*.csv"))

if not customer_email_files:

    st.info(
        "Customer emails CSV file is not available yet."
    )

else:

    for output_file in customer_email_files:

        with open(output_file, "rb") as file:

            st.download_button(
                label=f"⬇️ {output_file.name}",
                data=file,
                file_name=output_file.name,
                mime="text/csv"
            )

summary_files = list(SUMMARY_OUTPUT_DIR.glob("*.csv"))

if not summary_files:

    st.info(
        "Customer complaint summary CSV file is not available yet."
    )

else:

    for output_file in summary_files:

        with open(output_file, "rb") as file:

            st.download_button(
                label=f"⬇️ {output_file.name}",
                data=file,
                file_name=output_file.name,
                mime="text/csv"
            )