from app.models import CashWialon
from app.modules import my_time
from app.reports import ReportObject


class WialonReport(ReportObject):
    name = "wialon"
    headers = ['wialon_id', 'uNumber', 'uid', 'last_time', 'last_pos_time', 'x', 'y']

    def processing(self):
        query = self.db_session.query(CashWialon).all()
        for row in query:
            self.values.append([
                row.id,
                row.nm or '',
                row.uid or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                my_time.unix_to_moscow_time(row.last_pos_time) or '',
                row.pos_x or '',
                row.pos_y or ''
            ])