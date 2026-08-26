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

    with open("prompts/complaint_extraction_prompt.txt", "r", encoding="utf-8") as file:
        complaint_extraction_prompt = file.read()

    complaint_extraction_file_path = config.PROJECT_ROOT / "data" / "input" / "complaint_001.txt"

    response = llm.parse_document_with_llm(document_prompt=complaint_extraction_prompt,
                                file_path=complaint_extraction_file_path,
                                response_format=CustomerComplaintDetails)

    if(response['success']):
        print(response["content"].model_dump())
    else:
        print(response)
    
test_document_schema_extraction()