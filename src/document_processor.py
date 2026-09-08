from tqdm.auto import tqdm
from src.llm_manager import llm
from src.logger import logger

def process_documents(complaints_doc_df, extraction_prompt, system_prompt, response_format, default_response):

    results = []

    for index, row in tqdm(complaints_doc_df.iterrows(), total=len(complaints_doc_df), desc="Processing Customer Complaint FIles..."):

        try:
            response = llm.parse_document_with_llm(
                document_prompt=extraction_prompt,
                system_prompt=system_prompt,
                file_path=row['file_path'],
                response_schema=response_format
            )

            if response["success"]:
                results.append(response["content"].model_dump())
                complaints_doc_df.loc[index,"parse_status"] = "Completed"
            else:
                results.append(default_response)
                complaints_doc_df.loc[index,"parse_status"] = "Failed"

        except Exception as e:
            logger.error(f"Document Processor > Process Document > Failed : {e}")
            results.append(default_response)
            complaints_doc_df.loc[index,"parse_status"] = f"Failed : {e}"

    return complaints_doc_df, results