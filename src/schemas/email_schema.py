from pydantic import BaseModel, Field

class EmailBodySchema(BaseModel):
    """
    Structured output for email body
    """
    email_subject: str = Field(
        description = "Suitable Subject for Email."
    )

    email_body: str = Field(
        description = "Email body containing customer complaint information"
    )