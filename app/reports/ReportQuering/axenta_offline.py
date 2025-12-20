from app.models import CashAxenta
from app.modules import my_time
from app.reports import ReportObject


class AxentaOfflineReport(ReportObject):
    headers = ['axenta_id', 'name', 'uid', 'last_time', 'last_pos_time', 'x', 'y']
    name = "axenta_offline"
    localization_name = 'Давно offlice (от 3 дней)'
    category = 'axenta'

    def processing(self):
        three_days_ago = my_time.get_time_minus_three_days()
        query = self.db_session.query(CashAxenta).filter(CashAxenta.last_time < three_days_ago).all()
        for row in query:
            self.values.append([
                row.id or '',
                row.nm or '',
                row.uid or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                my_time.unix_to_moscow_time(row.last_pos_time) or '',
                row.pos_x or '',
                row.pos_y or ''
            ])

        self.filter_by_transport_access('name')