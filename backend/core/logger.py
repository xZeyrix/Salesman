import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(
        "app.log", 
        maxBytes=10*1024*1024, 
        backupCount=5, 
        encoding="utf-8"
    )

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[console_handler, file_handler]
    )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)
