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
        self.system_prompt = "You are a file parser expert. " \
            "You identify the fields that are required and returns it " \
            "in expected response format."
        self.email_system_prompt = """You are a professional customer service email writer.
                                    Based on the provided complaint details, generate:
                                        1. A clear, concise email subject.
                                        2. A professional and empathetic email body."""
        self.case_summary_system_prompt = """You are a professional case summary writer.
                                             Based on the provided complaint details, generate:
                                             1. A clear case summary report.
                                             2. Provide all expected details.
                                             3. Maintain professional and empathetic tone."""

    # text completion
    def parse_document_with_llm(self, document_prompt:str, file_path:Path, response_schema=None):
        """
        Performs standard chat completion.
        """

        uploaded_file = self.client.files.create(
            file=file_path,
            purpose="user_data"
        )

        print(uploaded_file)

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

        logger.info(f"Processing document for parsing response {file_path}")

        # The responses API expects input as an array of messages
        # First message is system, then the user prompt with file + text
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        logger.info("Started text completion request.")

        # structured output or normal output

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

    def chat_completion(
        self,
        user_email_prompt: str,
        response_schema=None,
    ):
        """
        Performs a standard text completion.
        """

        messages = [
            {
                "role": "system",
                "content": self.email_system_prompt,
            },
            {
                "role": "user",
                "content": user_email_prompt,
            },
        ]

        logger.info("Starting text completion request.")

        # --------------------------------------------------
        # Structured Output
        # --------------------------------------------------

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

    def case_summary_report(
        self,
        case_summary_prompt: str,
        response_schema=None,
    ):
        """
        Performs a standard text completion.
        """

        messages = [
            {
                "role": "system",
                "content": self.case_summary_system_prompt,
            },
            {
                "role": "user",
                "content": case_summary_prompt,
            },
        ]

        logger.info("Starting text completion request.")

        # --------------------------------------------------
        # Structured Output
        # --------------------------------------------------

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
llm = LLMManager()