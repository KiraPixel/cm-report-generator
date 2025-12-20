from app.models import reports_custom_transport_transfer
from app.reports import ReportObject


class CustomTransportTransferReport(ReportObject):
    headers = ['номер_лота', 'склад', 'регион', 'тип', 'модель_техники',
               'дата_перемещения', 'виалон_количество', 'виалон_онлайн', 'цезарь_количество', 'пресет_ид', 'пресет_имя']
    name = "custom_transport_transfer"
    localization_name = "Перемещения транспорта"
    category = 'reports_operator'
    configuration = {
                        "date_from": {"type": "date", "label": "Дата от"},
                        "date_to": {"type": "date", "label": "Дата до"},
                        "region": {
                            "type": "text",
                            "label": "Регион",
                            "placeholder": "Название региона"
                        },
                        "only_home_storages": {"type": "checkbox", "label": "Только Домашние склады"}
                    }
    isRoutineReport = True

    def processing(self):
        start_date = self.parameters.get('date_from'),
        end_date = self.parameters.get('date_to'),
        region = self.parameters.get('region', 'Химки'),
        home_storage = self.parameters.get('only_home_storages', 0)

        query = reports_custom_transport_transfer(
            self.db_session,
            start_date=start_date[0],
            end_date=end_date[0],
            region=region[0],
            home_storage=home_storage,
        )

        for row in query:
            self.values.append([
                row.get('номер_лота', ''),
                row.get('склад', ''),
                row.get('регион', ''),
                row.get('тип', ''),
                row.get('модель_техники', ''),
                row.get('дата_перемещения', ''),
                row.get('виалон_количество', ''),
                row.get('виалон_онлайн', ''),
                row.get('цезарь_количество', ''),
                row.get('пресет_ид', ''),
                row.get('пресет_имя', '')
            ])

        self.filter_by_transport_access('номер_лота')
        self.finish_processing()