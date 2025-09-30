from app.models import reports_custom_transport_transfer
from app.reports import ReportObject


class CustomTransportTransferReport(ReportObject):
    name = "custom_transport_transfer"
    localization_name = "Перемещения транспорта"
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
    headers = ['номер_лота', 'склад', 'регион', 'тип', 'модель_техники',
               'дата_перемещения', 'виалон_количество', 'виалон_онлайн', 'цезарь_количество', 'пресет_ид', 'пресет_имя']
    isRoutineReport = True

    def processing(self):
        start_date = self.parameters.get('date_from'),
        end_date = self.parameters.get('date_to'),
        region = self.parameters.get('region', 'Химки'),
        home_storage = self.parameters.get('only_home_storages', 0)

        print(start_date, end_date, region, home_storage)

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

        self.finish_processing()