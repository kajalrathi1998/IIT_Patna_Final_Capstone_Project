# check logger
# from src.logger import logger

# def check_logging():
#     logger.info("Testing log file.")
#     logger.error("This is error log.")

# check_logging()

# ----------------------------------------------------

# check discover file
# from src.utils import discover_files
# from src.config import config
# df = discover_files(config.PROJECT_ROOT / "data/input", ["*.txt"])
# print(df.head())

# ----------------------------------------------------

from src.llm_manager import llm
from src.config import config
from src.schemas.complaint_schema import CustomerComplaintDetails

def test_document_schema_extraction():

    with open("prompts/parser_system_prompt.txt", "r", encoding="utf-8") as file:
        parser_system_prompt = file.read()

    with open("prompts/complaint_extraction_prompt.txt", "r", encoding="utf-8") as file:
        complaint_extraction_prompt = file.read()

    complaint_extraction_file_path = config.PROJECT_ROOT / "data" / "input" / "complaint_001.txt"

    response = llm.parse_document_with_llm(document_prompt=complaint_extraction_prompt,
                                system_prompt=parser_system_prompt,
                                file_path=complaint_extraction_file_path,
                                response_schema=CustomerComplaintDetails)

    if(response['success']):
        print(response["content"].model_dump())
    else:
        print(response)

    return response["content"].model_dump()
    
# test_document_schema_extraction()


# ----------------------------------------------------


from src.llm_manager import llm
from src.config import config
from src.schemas.complaint_schema import CustomerComplaintDetails
from src.schemas.email_schema import EmailBodySchema
from src.email import send_email

def test_email_body_gen():

    with open("prompts/parser_system_prompt.txt", "r", encoding="utf-8") as file:
        parser_system_prompt = file.read()

    with open("prompts/email_system_prompt.txt", "r", encoding="utf-8") as file:
        email_system_prompt = file.read()

    with open("prompts/customer_email_prompt.txt", "r", encoding="utf-8") as file:
        email_extraction_prompt = file.read()

    with open("prompts/complaint_extraction_prompt.txt", "r", encoding="utf-8") as file:
        complaint_extraction_prompt = file.read()

    complaint_extraction_file_path = config.PROJECT_ROOT / "data" / "input" / "complaint_002.pdf"

    response = llm.parse_document_with_llm(document_prompt=complaint_extraction_prompt,
                                system_prompt=parser_system_prompt,
                                file_path=complaint_extraction_file_path,
                                response_schema=CustomerComplaintDetails)

    if(response['success']):
        customer_complaint = response["content"].model_dump()
    else:
        raise ValueError("llm response failed")
    
    customer_email_address = customer_complaint["customer_email"]

    
    email_prompt = email_extraction_prompt.format(customer_complaint = customer_complaint)

    result = llm.chat_completion(user_prompt = email_prompt,
                                system_prompt=email_system_prompt,
                                response_schema=EmailBodySchema)
    if(result['success']):
        print(result["content"].model_dump())
    else:
        print(result)
    
    email_body = result["content"].model_dump()["email_body"]
    email_subject = result["content"].model_dump()["email_subject"]

    return customer_email_address, email_body, email_subject

test_email_body_gen()  

# ----------------------------------------------------


def test_send_email():
    customer_email_address, email_body, email_subject = test_email_body_gen()
    sent_email = send_email(to_email=customer_email_address, subject=email_subject, body=email_body)

    print(f"{sent_email} email sent successfully")

#test_send_email()


# ----------------------------------------------------
from src.schemas.case_summary_schema import CaseSummary

def test_case_summary_gen():

    with open("prompts/summary_system_prompt.txt", "r", encoding="utf-8") as file:
        summary_system_prompt = file.read()

    with open("prompts/case_summary_prompt.txt", "r", encoding="utf-8") as file:
        case_summary_prompt = file.read()
    
    customer_complaint = test_document_schema_extraction()
    case_summary_final_prompt = case_summary_prompt.format(customer_case=customer_complaint)

    response = llm.chat_completion(user_prompt=case_summary_final_prompt,
                                   system_prompt=summary_system_prompt, 
                                   response_schema=CaseSummary)

    if(response['success']):
        print(response["content"].model_dump())
    else:
        print(response)


test_case_summary_gen()

    
