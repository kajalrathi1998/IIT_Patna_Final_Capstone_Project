from pathlib import Path

from openai import OpenAI

from src.config import config
from src.cost_tracker import cost_tracker
from src.logger import logger

class LLMManager:
    """
    Centralized OpenAI inference manager.

    All interactions with OpenAI should go through this class.
    """

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    # text completion
    def parse_document_with_llm(self, document_prompt:str, system_prompt:str, file_path:Path, response_schema=None):
        """
        Performs document details extraction
        """
        # Ensure file_path is a Path object (handles both str and Path inputs)
        file_path = Path(file_path)

        uploaded_file = self.client.files.create(
            file=file_path,
            purpose="user_data"
        )

        user_prompt = [
            {
                "type": "input_file",
                "file_id": uploaded_file.id
            },
            {
                "type": "input_text",
                "text": document_prompt
            }
        ]

        logger.info(f"Processing document {file_path}")

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        logger.info("Started document parsing request.")

        # structured output or normal output
        return self.get_structured_output(response_schema, messages)

    def chat_completion(
        self,
        user_prompt,
        system_prompt: str,
        response_schema=None,
    ):
        """
        Performs a standard text completion with structured output.
        """

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        logger.info("Starting chat completion request.")

        # structured output or normal output
        return self.get_structured_output(response_schema, messages)

    def get_structured_output(self, response_schema, messages):

        try:
            if response_schema:
                    
                response = self.client.responses.parse(
                    model=config.MODELS["document_model"],
                    input=messages,
                    text_format=response_schema,
                )

                content = response.output_parsed

            else:

                response = self.client.responses.create(
                    model=config.MODELS["document_model"],
                    input=messages,
                    temperature=config.MODELS["temperature"],
                    max_output_tokens=config.MODELS["max_tokens"],
                )

                content = response.output_text

            logger.info("Text completion request completed.")

            usage = response.usage

            cost = cost_tracker.calculate_cost(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens
            )

            logger.info(
                f"Model={config.MODELS['document_model']} | "
                f"Input Tokens={cost['input_tokens']} | "
                f"Output Tokens={cost['output_tokens']} | "
                f"Total cost={cost['current_total_cost']} {cost['currency']} | "
            )

            return {
                "success": True,
                "content": content,
                "usage": cost,
                "model": config.MODELS["document_model"],
            }
        except Exception as e:
            logger.error(f"Failed with error : {e}")
            return {
                "success": False,
                "content": f"Failed {e}" ,
                "usage": None,
                "model": config.MODELS["document_model"],
            }

llm = LLMManager()