from pathlib import Path
import os

import toml
from dotenv import load_dotenv

class Config:
    """
    Loads the project configuration from .env file and config.toml file.
    """

    def __init__(self):

        self.PROJECT_ROOT = Path(__file__).resolve().parent.parent
        self.tomlFile = self.PROJECT_ROOT / "config.toml"
        self.envFile = self.PROJECT_ROOT / ".env"

        load_dotenv(self.envFile)

        self.config = toml.load(self.tomlFile)

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured in .env")

        self.MODELS = self.config["models"]

        #self.RETRY = self.config["retry"]

        #self.RATE_LIMIT = self.config["rate_limit"]

        self.TOKEN_LIMIT = self.config["token_limit"]

        self.COST = self.config["cost"]

        self.LOGGING = self.config["logging"]

        self.PATHS = self.config["paths"]

config = Config()