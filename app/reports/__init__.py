import logging
import time

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.models import Reports, User
from app.modules import my_time, generate_excel_report
from app.modules.location_module import get_address_from_coords
from app.modules.mail_sender import send_email
from app.modules.my_time import now_unix_time

logger = logging.getLogger('cm_report_generator')

class ReportObject:
    name = None
    headers = None
    heavy_report = None
    localization_name = None
    configuration = None
    isRoutineReport = None
    parameters = None

    def __init__(self, db_session: Session, report_id: int or None, username: str, parameters = None) -> None:
        self.name = self.__class__.name if self.__class__.name else None
        self.headers = list(self.__class__.headers) if self.__class__.headers else None
        self.heavy_report = bool(self.__class__.heavy_report) if self.__class__.heavy_report else False
        self.name = self.__class__.localization_name if self.__class__.localization_name else None
        self.configuration = dict(self.__class__.configuration) if self.__class__.configuration else None
        self.isRoutineReport = bool(self.__class__.isRoutineReport) if self.__class__.isRoutineReport else False
        self.id = None
        self.db_object = None
        self.status = 'new'
        self.start_date = None
        self.updated_date = None
        self.end_date = None
        self.configuration = None
        self.percentage_completed = 0
        self.user: User = None
        self.owner_name = None
        self.isValid = False
        self.isSuccess = None
        self.db_session: Session = None
        self.error = ''
        self.values: list = []

        logger.info(f"Инициализация ReportObject с report_id={report_id}, username={username}")
        self.owner_name = username
        self.db_session = db_session
        self.parameters = parameters

        if not report_id:
            if not self.owner_name:
                logger.error("Не указан username при создании нового отчета")
                self.finish_processing(False, 'Username is required')
                return
            logger.debug("Создание нового отчета в базе данных")
            self.create_to_db()
        else:
            self.id = report_id

        self.get_from_db()
        if not self.db_object:
            logger.error(f"Отчета с id={self.id} не существует")
            return

        if self.status == 'finish':
            logger.error(f"Отчет {self.id} уже обработан")
            return

        self.get_user()
        if not self.user:
            logger.error(f"Пользователь с username={self.owner_name} не найден")
            self.start_date = now_unix_time()
            self.finish_processing(False, 'User is not found')
            return

        self.start_date = now_unix_time()
        logger.info(f"Начало обработки отчета id={self.id}, status=processing")
        self.update_status('processing')
        if self.isRoutineReport:
            if self.parameters is None:
                self.isValid = False
                self.finish_processing(False, 'Параметры отчета не предоставлены')
                return

        self.isValid = True

        try:
            logger.info(f"Запуск обработки отчета id={self.id}")
            self.percentage_completed = 50
            if self.heavy_report:
                self.percentage_completed = 0
            self.update_to_db()
            self.processing()
            logger.info(f"Завершение обработки отчета id={self.id}")
            self.finish_processing()
        except Exception as e:
            logger.error(f"Ошибка при обработке отчета id={self.id}: {str(e)}")
            self.isValid = False
            self.finish_processing(False, f"Ошибка обработки: {str(e)}")

    def processing(self):
        logger.debug(f"Начало метода processing для отчета id={self.id}")
        self.isValid = False
        self.isSuccess = False
        self.update_status('failure')
        logger.warning(f"Отчет id={self.id} помечен как failure")

    def update_status(self, new_status):
        logger.debug(f"Обновление статуса отчета id={self.id} на {new_status}")
        self.status = new_status
        self.update_to_db()

    def finish_processing(self, fn_success=True, fn_error=''):
        logger.info(f"Завершение обработки отчета id={self.id}, успех={fn_success}, ошибка={fn_error}")
        if not fn_success:
            self.isSuccess = False
            self.error = fn_error
            logger.error(f"Ошибка в отчете id={self.id}: {fn_error}")
        else:
            self.isSuccess = True
            self.isValid = True

        self.end_date = now_unix_time()
        self.percentage_completed = 100
        self.update_status('finish')
        self.update_to_db()
        logger.debug(f"Отчет id={self.id} завершен, статус сохранен в базе данных")

    def create_to_db(self):
        logger.debug(f"Создание записи отчета для username={self.owner_name}")
        self.db_object = Reports(
            username=self.owner_name,
            type=self.name,
            status=self.status,
            parameters=self.parameters,
            success=self.isSuccess
        )
        self.db_session.add(self.db_object)
        self.db_session.commit()
        self.id = self.db_object.id
        logger.info(f"Создан отчет с id={self.id} в базе данных")

    def get_from_db(self):
        logger.info(f"Получение отчета id={self.id} из базы данных")
        self.db_object = self.db_session.query(Reports).filter_by(id=self.id).first()
        if self.db_object:
            self.id = self.db_object.id
            self.name = self.db_object.type
            self.owner_name = self.db_object.username
            self.status = self.db_object.status
            self.parameters = self.db_object.parameters
            logger.debug(f"Данные отчета id={self.id} успешно получены")

    def update_to_db(self):
        logger.debug(f"Обновление данных отчета id={self.id} в базе данных")
        self.updated_date = now_unix_time()
        self.db_object.type = self.name
        self.db_object.start_date = self.start_date
        self.db_object.updated_date = self.updated_date
        self.db_object.end_date = self.end_date
        self.db_object.username = self.owner_name
        self.db_object.status = self.status
        self.db_object.parameters = self.parameters
        self.db_object.percentage_completed = self.percentage_completed
        self.db_object.success = self.isSuccess
        self.db_object.errors = self.error
        self.db_session.commit()
        logger.debug(f"Данные отчета id={self.id} успешно обновлены")

    def to_xlsx(self):
        logger.debug(f"Генерация XLSX для отчета id={self.id}")
        if not self.isValid:
            logger.warning(f"Отчет id={self.id} не валиден, XLSX не сгенерирован")
            return None
        result = generate_excel_report.start(self.headers, self.values)
        logger.info(f"XLSX успешно сгенерирован для отчета id={self.id}")
        return result

    def to_json(self):
        logger.debug(f"Генерация JSON для отчета id={self.id}")
        if not self.isValid:
            logger.warning(f"Отчет id={self.id} не валиден, JSON не сгенерирован")
            return None
        json_result = {
            'field': self.values,
        }
        result = {
            'id': self.id,
            'name': self.name,
            'parameters': self.parameters,
            'status': self.status,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'isRoutineReport': self.isRoutineReport,
            'username': self.user.username,
            'isValid': self.isValid,
            'isSuccess': self.isSuccess,
            'error': self.error,
            'json_result': json_result
        }
        logger.info(f"JSON успешно сгенерирован для отчета id={self.id}")
        return result

    def get_user(self):
        logger.debug(f"Получение пользователя с username={self.owner_name}")
        try:
            self.user = self.db_session.query(User).filter_by(username=self.db_object.username).first()
        except Exception as e:
            logger.error(f"Ошибка при получении отчета id={self.id}: {str(e)}")
            self.user = None

    def send_to_mail(self):
        logger.debug(f"Отправка отчета id={self.id} на email")
        if not self.isValid:
            logger.warning(f"Отчет id={self.id} не валиден, email не отправлен")
            return False
        result = send_email(
            target=self.user.email,
            subject=f'Отчет {self.name}',
            content=f'Во вложении заказанный отчет {self.name}',
            attachment_name=f'{self.name}-{self.end_date}.xlsx',
            attachment_content=self.to_xlsx(),
            session=self.db_session
        )
        if result:
            logger.info(f"Email с отчетом id={self.id} успешно отправлен на {self.user.email}")
        else:
            logger.error(f"Не удалось отправить email с отчетом id={self.id}")
        return result

    def get_location(self, x: float, y: float) -> str:
        """Получение адреса по координатам с механизмом повторных попыток."""
        logger.debug(f"Получение адреса по координатам ({x}, {y}) для отчета id={self.id}")
        if not self.isValid:
            logger.warning(f"Отчет id={self.id} не валиден, адрес не запрошен")
            return "Error convert"
        for attempt in range(50):  # MAX_ATTEMPTS
            try:
                location = str(get_address_from_coords(x, y, self.db_session))
                if location != "Time out to convert":
                    logger.debug(f"Адрес успешно получен: {location}")
                    return location
                logger.debug(f"Попытка {attempt + 1}: тайм-аут при получении адреса")
            except Exception as e:
                logger.error(f"Попытка {attempt + 1} из 50 не удалась: {e}")
            if attempt < 49:
                time.sleep(5)  # SLEEP_INTERVAL
        logger.error(f"Не удалось получить адрес после 50 попыток для координат ({x}, {y})")
        return "Error convert"  # DEFAULT_ADDRESS