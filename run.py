import os
import time
import logging

from app import job


int_level=logging.INFO
if os.getenv('DEV', 0) == 1:
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
    while True:
        logger.info("Попытка получение новых репортов.")
        job.work()
        time.sleep(10)