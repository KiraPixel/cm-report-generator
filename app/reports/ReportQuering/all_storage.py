from app.models import Storage
from app.reports import ReportObject


class StorageReport(ReportObject):
    headers = ['ID', 'Название', 'Тип', 'Регион', 'Адрес', 'Организация']
    name = "all_storage"
    localization_name = "Все склады"
    category = 'reports_operator'

    def processing(self):
        query = self.db_session.query(
            Storage.ID,
            Storage.name,
            Storage.type,
            Storage.region,
            Storage.address,
            Storage.organization
        ).all()
        for row in query:
            self.values.append([
                row.ID or '',
                row.name or '',
                row.type or '',
                row.region or '',
                row.address or '',
                row.organization or ''
            ])