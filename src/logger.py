import logging
from pathlib import Path

from src.config import config

def get_logger():

    log_file_path = Path(config.LOGGING["log_file"])

    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file_path,
        level=getattr(logging, config.LOGGING["log_level"]),
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    return logging.getLogger("logger")

logger = get_logger()
