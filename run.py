import os
import time
import logging
import threading
import uvicorn

from app import job
from app.api import app as fastapi_app

int_level=logging.INFO
if os.getenv('DEV', '0') == '1':
    int_level = logging.DEBUG

logging.basicConfig(
    level=int_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('cm_report_generator')

if __name__ == "__main__":
    logger.info("Запуск планировщика задач...")
    logger.debug("ВНИМАНИЕ! ЗАПУСК В DEBUG РЕЖИМЕ!")

    # === Запускаем FastAPI в отдельном daemon-потоке ===
    api_thread = threading.Thread(
        target=uvicorn.run,
        kwargs={
            "app": fastapi_app,
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": "info"
        },
        name="FastAPI-Thread"
    )
    api_thread.daemon = True
    api_thread.start()
    logger.info("API сервер запущен → http://localhost:8000/docs")

    while True:
        logger.info("Попытка получения новых репортов.")
        job.work()
        time.sleep(60)