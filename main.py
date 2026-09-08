# define import and paths
from pathlib import Path
from tqdm.auto import tqdm

import sys
import shutil
import warnings
import pandas as pd

from src.config import config
from src import utils
from src.llm_manager import llm
from src.schemas.complaint_schema import CustomerComplaintDetails
from src.schemas.email_schema import EmailBodySchema
from src.schemas.case_summary_schema import CaseSummary
from src.email import send_email
from src.document_processor import process_documents
from src.logger import logger

warnings.filterwarnings("ignore")

# paths
PROJECT_ROOT = Path(__file__).resolve().parent

print(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

INPUT_DOCUMENT_DIR = PROJECT_ROOT / config.PATHS['document_input']
PROCESSED_DOCUMENT_DIR = PROJECT_ROOT / config.PATHS['document_input_processed']
STRUCTURED_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['structured_data_dir']
EMAIL_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['email_data_dir']
SUMMARY_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['summary_data_dir']
OUTPUT_DATA_DIR = PROJECT_ROOT / config.PATHS['final_output']
PROMPTS_DIR = PROJECT_ROOT / "prompts"

def main(number_of_files=None):

    try:
        # read prompts
        parser_system_prompt, complaint_extraction_prompt, email_system_prompt, email_extraction_prompt,case_summary_prompt, summary_system_prompt = initialize()

        # parse customer complaint document
        logger.info("Pipeline : Started extracting documents")
        complaints_document_df = process_complaint_documents(parser_system_prompt, complaint_extraction_prompt, number_of_files)

        # write email content for customer
        logger.info("Pipeline : Started generating emails")
        email_df = generate_emails_for_complaints(complaints_document_df, email_system_prompt, email_extraction_prompt)

        # send email to customer
        logger.info("Pipeline : Started sending emails")
        email_result_df = send_email_to_customers(email_df)

        # generate case summaries report
        logger.info("Pipeline : Started generating summary")
        summary_df = generate_customer_complaint_summary(email_result_df,case_summary_prompt,summary_system_prompt)

        # save final report
        save_final_report(summary_df)

    except Exception as e :
        print(f"Pipeline failed : {e}")
        raise

def initialize():

    OUTPUT_DATA_DIR.mkdir(parents=True,exist_ok=True)
    PROCESSED_DOCUMENT_DIR.mkdir(parents=True,exist_ok=True)
    STRUCTURED_OUTPUT_DIR.mkdir(parents=True,exist_ok=True)
    EMAIL_OUTPUT_DIR.mkdir(parents=True,exist_ok=True)
    SUMMARY_OUTPUT_DIR.mkdir(parents=True,exist_ok=True)
    OUTPUT_DATA_DIR.mkdir(parents=True,exist_ok=True)

    parser_system_prompt= utils.load_prompt(PROMPTS_DIR / "parser_system_prompt.txt" )
    complaint_extraction_prompt = utils.load_prompt(PROMPTS_DIR / "complaint_extraction_prompt.txt" )
    email_system_prompt = utils.load_prompt(PROMPTS_DIR / "email_system_prompt.txt" )
    email_extraction_prompt = utils.load_prompt(PROMPTS_DIR / "customer_email_prompt.txt" )
    case_summary_prompt = utils.load_prompt(PROMPTS_DIR / "case_summary_prompt.txt" )
    summary_system_prompt = utils.load_prompt(PROMPTS_DIR / "summary_system_prompt.txt" )

    return parser_system_prompt, complaint_extraction_prompt, email_system_prompt, email_extraction_prompt,case_summary_prompt,summary_system_prompt

def process_complaint_documents(parser_system_prompt, complaint_extraction_prompt, number_of_files):

    complaints_doc_df = utils.discover_files(input_dir=INPUT_DOCUMENT_DIR, number_of_files=number_of_files)
    empty_complaint = {
        "customer_name" : None,
        "customer_email" : None,
        "customer_phone" : None,
        "complaint_category" : None,
        "complaint_description" : None,
        "resolution_provided" : None,
        "escalation_information" : None,
        "supporting_information" : None,
        "current_status": None 
    }

    logger.info(f"Pipeline > process_complaint_documents : processing {len(complaints_doc_df)} customer complaints")
    complaints_doc_df, results = process_documents(
        complaints_doc_df=complaints_doc_df,
        extraction_prompt=complaint_extraction_prompt,
        system_prompt=parser_system_prompt,
        response_format=CustomerComplaintDetails,
        default_response=empty_complaint
    )

    # save structured data
    structured_document_df = pd.concat([complaints_doc_df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    output_file = STRUCTURED_OUTPUT_DIR / "complaint_structured_data.csv"
    utils.save_dataframe(structured_document_df, output_file)
    logger.info(f"Pipeline > process_complaint_documents : Saved structured output to {output_file}")

    # structured data for processing
    final_complaint_df = complaints_doc_df.reset_index(drop=True)
    final_complaint_df["complaint_object"] = results

    return final_complaint_df

def generate_emails_for_complaints(complaints_document_df, email_system_prompt, email_extraction_prompt):

    complaints_document_df["email_generation"] = "Pending"
    results = []
    empty_email ={
        "email_subject":None,
        "email_body":None
    }
    email_df = pd.DataFrame()

    for index, row in tqdm(complaints_document_df.iterrows(), total=len(complaints_document_df), desc="Generating email content for customer..."):

        customer_complaint = row['complaint_object']
        email_df.loc[index,"customer_name"] = customer_complaint['customer_name']
        email_df.loc[index,"customer_email"] = customer_complaint['customer_email']
        email_df.loc[index,"email_subject"] = None
        email_df.loc[index,"email_body"] = None
        
        try: 
            email_prompt = email_extraction_prompt.format(customer_complaint=customer_complaint)

            response = llm.chat_completion(
                user_prompt=email_prompt,
                system_prompt=email_system_prompt,
                response_schema=EmailBodySchema
            )

            if response["success"]:
                email_object = response["content"].model_dump()
                results.append(email_object)
                complaints_document_df.loc[index,"email_generation"] = "Completed"
                email_df.loc[index,"email_subject"] = email_object['email_subject']
                email_df.loc[index,"email_body"] = email_object['email_body']
            else:
                results.append(empty_email)
                complaints_document_df.loc[index,"email_generation"] = "Failed"
                
        except Exception as e:
            logger.error(f"Pipeline > generate_emails_for_complaints > Failed : {e}")
            results.append(empty_email)
            complaints_document_df.loc[index,"email_generation"] = f"Failed : {e}"

    # save emails generated for customer
    output_file = EMAIL_OUTPUT_DIR / "complaint_email_data.csv"
    utils.save_dataframe(email_df, output_file)

    final_df = pd.concat([complaints_document_df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    # print(final_df.to_string())
    return final_df

def send_email_to_customers(email_df):

    email_df["email_sent"] = False

    for index, row in tqdm(email_df.iterrows(), total=len(email_df), desc="Sending emails to customer..."):
    
        try:
            complaint = row['complaint_object']

            email_sent = send_email(
                to_email= complaint['customer_email'],
                subject = row['email_subject'],
                body = row['email_body']
            )

            if email_sent:
                email_df.loc[index,"email_sent"] = True
            else:
                email_df.loc[index,"email_sent"] = False

        except Exception as e:
            logger.error(f"Pipeline > send_email_to_customers > Failed : {e}")
            email_df.loc[index,"email_sent"] = False

    return email_df

def generate_customer_complaint_summary(result_df, case_summary_prompt, summary_system_prompt):

    results = []
    empty_summary = {
        "case_overview" : None,
        "key_issue" : None,
        "action_taken" : None,
        "current_status" : None,
        "recommended_next_action" : None
    }
    result_df["summary_generation"] = "Pending"
    case_summary_df = pd.DataFrame()

    for index, row in tqdm(result_df.iterrows(), total=len(result_df), desc="Generating summary..."):

        complaint = row['complaint_object']
        case_summary_df.loc[index,"customer_name"] = complaint['customer_name']
        case_summary_df.loc[index,"customer_email"] = complaint['customer_email']

        try:
            email_content = {}

            if row['email_sent'] :
                email_content = {
                    "subject" : row['email_subject'],
                    "body" : row['email_body']
                }

            case_summary_final_prompt = case_summary_prompt.format(
                customer_case=complaint,
                email_sent=row['email_sent'],
                email_content=email_content  
            )

            response = llm.chat_completion(
                user_prompt=case_summary_final_prompt, 
                system_prompt=summary_system_prompt,
                response_schema=CaseSummary
            )

            if response["success"]:
                results.append(response["content"].model_dump())
                result_df.loc[index,"summary_generation"] = "Completed"
            else:
                results.append(empty_summary)
                result_df.loc[index,"summary_generation"] = "Failed"

        except Exception as e:
            logger.error(f"Pipeline > generate_customer_complaint_summary > Failed : {e}")
            results.append(empty_summary)
            result_df.loc[index,"summary_generation"] = f"Failed : {e}"

    case_summary_final = pd.concat([case_summary_df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    output_file = SUMMARY_OUTPUT_DIR / "complaint_case_summaries.csv"
    utils.save_dataframe(case_summary_final, output_file)

    # structured data for processing
    result_df= pd.concat([result_df.reset_index(drop=True), pd.DataFrame(results)], axis=1)

    return result_df

def save_final_report(report_df):

    for index, row in tqdm(report_df.iterrows(), total=len(report_df), desc="Saving final report..."):

        try:
            if (row['email_sent']):
                current_path = str(row['file_path'])
                source = Path(current_path)
                destination = Path(current_path.replace("input", "input/processed"))
                report_df.loc[index,"file_path"] = current_path.replace("input", "input/processed")
                shutil.move(source, destination)

        except Exception as e:
            logger.error(f"Pipeline > save_final_report > Failed : {e}")

    output_file = OUTPUT_DATA_DIR / "final_report.csv"
    utils.save_dataframe(report_df, output_file)

if __name__ == "__main__":
    main()