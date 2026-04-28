import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # Создаем обработчики
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(
        "app.log", 
        maxBytes=10*1024*1024, 
        backupCount=5, 
        encoding="utf-8" 
    )
    

    # Настраиваем базовый конфиг
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[console_handler, file_handler],
        force=True  # Важно: переписывает настройки, если они уже были заданы uvicorn
    )

    # Привязываем логгеры uvicorn к нашим обработчикам
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        log = logging.getLogger(logger_name)
        log.handlers = [console_handler, file_handler]
        log.propagate = False  # Чтобы логи не дублировались

    # SQLAlchemy оставляем тихим
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)
