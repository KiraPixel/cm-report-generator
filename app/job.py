import logging
import os
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import worker
from app.models import Reports
from app.modules import my_time
from app.modules.my_time import now_unix_time
from app.reports import ReportObject
from app.reports.ReportQuering import get_report_class

active_threads = []
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///default.db')
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger('cm_report_generator')
obsolescence_time_minute = 20



def get_new_reports(session: SessionLocal):
    query = session.query(Reports).filter(Reports.status == 'new').all()
    return query

def get_stopped_reports(session: SessionLocal):
    query = session.query(Reports).filter(Reports.status == 'processing', Reports.updated_date <= my_time.teen_minutes_ago_unix()).all()
    return query

def get_schedule_reports(session: SessionLocal):
    query = session.query(Reports).filter(Reports.status == 'schedule').all()
    return query

def close_with_error(session: SessionLocal, report_object: Reports, error_text):
    try:
        report_object.status = 'error'
        report_object.percentage_completed=0
        report_object.end_date = now_unix_time()
        report_object.error_msg = error_text
        session.commit()

        return True
    except Exception as e:
        session.rollback()
        logger.error(f'close_with_error закончился с ошибкой: {e}')
        return False

def create_new_worker(report_query: Reports, report_instance: ReportObject, not_api_report=True):
    try:
        SessionWorker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        thread = threading.Thread(
            target=worker.start,
            args=(report_query, report_instance, SessionWorker(), None, None, None, not_api_report),
            name=f"Worker-Thread-{report_query.id}"
        )
        thread.daemon = True
        thread.start()
        active_threads.append(thread)
        logger.info(f"Запущен поток для отчета {report_query.id}: {thread.name}")
    except Exception as e:
        logger.error(f"Ошибка при создании потока для отчета {report_query.id}: {e}")
        close_with_error(SessionLocal(), report_query, f"Ошибка создания потока: {str(e)}")


def work():
    session = SessionLocal()
    try:
        new_report = get_new_reports(session)
        stopper_report = get_stopped_reports(session)
        schedule_report = get_schedule_reports(session)
        logger.info(f'Найдено новых отчетов: {len(new_report)}')
        logger.info(f'Найдено новых остановившихся: {len(stopper_report)}')
        logger.info(f'Найдено запланированных отчетов: {len(schedule_report)}')

        for report in new_report:
            report_class = get_report_class(report.type)
            if report_class is None:
                logger.info(f'Фейковый отчет {report.id}')
                close_with_error(session, report, 'Отчет не найден')
            else:
                logger.info(f'Обработка нового отчета {report.id}')
                create_new_worker(report, report_class)

        for report in stopper_report:
            report_class = get_report_class(report.type)
            if report_class is None:
                close_with_error(session, report, 'Ошибка при возобновлении отчета')
            else:
                create_new_worker(report, report_class)

        for report in schedule_report:
            report_class = get_report_class(report.type)
            if report_class is None:
                close_with_error(session, report, 'Отчет не найден')
            else:
                if report.start_date is None or report.start_date <= now_unix_time():
                    create_new_worker(report, report_class)

    finally:
        session.close()

    # Очистка завершенных потоков
    global active_threads
    active_threads = [t for t in active_threads if t.is_alive()]
    logger.info(f"Активных потоков: {len(active_threads)}")