from app.models import CashCesar
from app.modules import my_time
from app.reports import ReportObject


class CesarOfflineReport(ReportObject):
    headers = ['cesar_id', 'uNumber', 'PIN', 'last_time']
    name = "cesar_offline"
    localization_name = 'Давно offlice (от 3 дней)'
    category = 'cesar'

    def processing(self):
        three_days_ago = my_time.get_time_minus_three_days()
        query = self.db_session.query(CashCesar).filter(CashCesar.last_time < three_days_ago).all()
        for row in query:
            self.values.append([
                row.unit_id or '',
                row.object_name or '',
                row.pin or '',
                my_time.unix_to_moscow_time(row.last_time) or ''
            ])

        self.filter_by_transport_access('uNumber')