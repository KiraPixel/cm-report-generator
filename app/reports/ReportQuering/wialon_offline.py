from app.models import CashWialon
from app.modules import my_time
from app.reports import ReportObject


class WialonOfflineReport(ReportObject):
    headers = ['wialon_id', 'uNumber', 'uid', 'last_time', 'last_pos_time', 'x', 'y']
    name = "wialon_offline"
    localization_name = "Давно offline (от 3 дней)"
    category = 'wialon'

    def processing(self):
        three_days_ago = my_time.get_time_minus_three_days()
        query = self.db_session.query(CashWialon).filter(CashWialon.last_time < three_days_ago).all()
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

        self.filter_by_transport_access('uNumber')