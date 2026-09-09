# Customer Complaint Processing Pipeline

## About the Project

This is an **automated customer complaint processing pipeline** that uses LLMs (OpenAI GPT-4.1) to process customer complaint documents end-to-end. The pipeline:

1. **Extracts structured data** from complaint documents (PDF, text, etc.) — customer name, email, phone, complaint category, description, resolution, escalation info, supporting details, and current status
2. **Generates personalized response emails** for each customer based on their complaint details
3. **Sends emails** to customers via SMTP (Gmail)
4. **Creates case summaries** with overview, key issues, actions taken, current status, and recommended next actions
5. **Produces final reports** in CSV format for record-keeping

The project includes both a **CLI pipeline** (`main.py`) and a **Streamlit web UI** (`streamlit_app.py`) for batch processing with progress tracking and file downloads.

---

## Project Structure

```
work-branch/
├── main.py                    # CLI entry point for the pipeline
├── streamlit_app.py           # Streamlit web UI
├── config.toml                # Configuration (models, paths, logging, costs, email)
├── .env                       # Environment variables (API keys, email credentials)
├── prompts/                   # LLM prompt templates
│   ├── parser_system_prompt.txt
│   ├── complaint_extraction_prompt.txt
│   ├── email_system_prompt.txt
│   ├── customer_email_prompt.txt
│   ├── case_summary_prompt.txt
│   └── summary_system_prompt.txt
├── src/
│   ├── config.py              # Configuration loader
│   ├── logger.py              # Logging setup
│   ├── utils.py               # Utility functions (file discovery, prompt loading, CSV I/O)
│   ├── llm_manager.py         # LLM interaction (OpenAI structured outputs)
│   ├── document_processor.py  # Document processing pipeline
│   ├── email.py               # Email sending (SMTP)
│   └── schemas/
│       ├── complaint_schema.py      # Pydantic model for complaint extraction
│       ├── email_schema.py          # Pydantic model for email generation
│       └── case_summary_schema.py   # Pydantic model for case summaries
└── data/
    ├── input/                 # Place complaint documents here
    ├── input/processed/         # Processed files moved here
    └── output/
        ├── structured_data/     # complaint_structured_data.csv
        ├── customer_emails/     # complaint_email_data.csv
        ├── case_summaries/      # complaint_case_summaries.csv
        └── final_report.csv     # Consolidated final report
```

---

## How to Clone and Run Locally

### Prerequisites

- **Python 3.10+**
- **OpenAI API Key** (for GPT-4.1)
- **Gmail App Password** (for sending emails via SMTP)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd work-branch
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If `requirements.txt` doesn't exist, install the core dependencies manually:
>
> ```bash
> pip install openai pydantic pandas tqdm python-dotenv toml streamlit
> ```

### 4. Configure Environment Variables

Create a `.env` file in the project root (or copy from `.env.example` if available):

```env
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email credentials for SMTP (required for email sending)
sender_email=your-email@gmail.com
app_password=your-gmail-app-password
```

**To get a Gmail App Password:**

1. Enable 2-Factor Authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Use that 16-character password as `app_password`

### 5. Run the Pipeline

#### Option A: Streamlit Web UI (Recommended)

```bash
streamlit run streamlit_app.py
```

This opens a web interface at `http://localhost:8501` where you can:

- Upload multiple complaint files
- Set batch size for processing
- Monitor progress with a progress bar
- Download output CSV files (final report, structured complaints, emails, summaries)

#### Option B: CLI

```bash
python main.py
```

Processes all files in `data/input/` using default batch size. You can modify the `main()` call in `main.py` to pass a `number_of_files` parameter for batch processing.

---

## Input File Format

### Supported Formats

The pipeline accepts **any text-based document** that can be read as plain text:

- `.txt` — Plain text files
- `.pdf` — PDF documents (text extraction required)
- `.docx` — Word documents (text extraction required)
- Any other format supported by the document processor

### Expected Content Structure

Each input file should contain a **customer complaint** with the following information (the LLM will extract these fields):

| Field                            | Description                                                          | Required |
| -------------------------------- | -------------------------------------------------------------------- | -------- |
| **Customer Name**          | Full name or available name of the customer                          | Yes      |
| **Customer Email**         | Email address for response                                           | Yes      |
| **Customer Phone**         | Contact number (mobile/landline)                                     | No       |
| **Complaint Category**     | Category/type of complaint (e.g., "Billing", "Technical", "Service") | Yes      |
| **Complaint Description**  | Detailed description of the issue                                    | Yes      |
| **Resolution Provided**    | What resolution was offered/provided                                 | No       |
| **Escalation Information** | Any escalation details (ticket numbers, teams involved)              | No       |
| **Supporting Information** | Additional docs, references, evidence provided by customer           | No       |
| **Current Status**         | Current state (e.g., "Open", "In Progress", "Resolved", "Closed")    | No       |

### Example Input File (`complaint_001.txt`)

```
Customer Complaint Report
=========================

Customer Name: John Smith
Customer Email: john.smith@email.com
Customer Phone: +1-555-0123

Complaint Category: Billing
Complaint Description: I was charged $99.99 for a premium subscription I never signed up for. The charge appeared on my credit card statement dated March 15, 2024. I have been a basic plan user for 2 years and never requested an upgrade.

Resolution Provided: Refund initiated for $99.99, subscription downgraded to basic plan.

Escalation Information: Escalated to Billing Team (Ticket #BILL-2024-001234)

Supporting Information: Credit card statement attached showing unauthorized charge. Screenshot of account settings showing basic plan.

Current Status: In Progress
```

### Placing Input Files

1. Place your complaint files in the **`data/input/`** directory
2. The Streamlit UI also allows uploading files directly via the web interface
3. After processing, files are automatically moved to **`data/input/processed/`**

---

## Output Files

| File                              | Location                         | Description                                                        |
| --------------------------------- | -------------------------------- | ------------------------------------------------------------------ |
| `complaint_structured_data.csv` | `data/output/structured_data/` | Extracted complaint fields                                         |
| `complaint_email_data.csv`      | `data/output/customer_emails/` | Generated email subject & body per customer                        |
| `complaint_case_summaries.csv`  | `data/output/case_summaries/`  | Case summaries with overview, key issues, actions, recommendations |
| `final_report.csv`              | `data/output/`                 | Consolidated report with all data                                  |

---

## Configuration

Key settings in `config.toml`:

```toml
[models]
document_model = "gpt-4.1"     # LLM model to use
temperature = 0.0              # Deterministic outputs
max_tokens = 2048              # Max output tokens

[paths]
document_input = "data/input"
document_input_processed = "data/input/processed"
structured_data_dir = "data/output/structured_data"
email_data_dir = "data/output/customer_emails"
summary_data_dir = "data/output/case_summaries"
final_output = "data/output"

[email]
enabled = true
smtp_host = "smtp.gmail.com"
smtp_port = 587
from_name = "Service Team"
```

---

## Troubleshooting

| Issue                             | Solution                                                  |
| --------------------------------- | --------------------------------------------------------- |
| `OPENAI_API_KEY not configured` | Add your OpenAI API key to`.env`                        |
| Email sending fails               | Verify Gmail App Password and 2FA is enabled              |
| No files processed                | Ensure files are in`data/input/` or uploaded via UI     |
| `ModuleNotFoundError`           | Run`pip install -r requirements.txt` in activated venv  |
| Permission errors on Windows      | Run terminal as Administrator or check folder permissions |

---

## License

This project is for educational/demo purposes.
