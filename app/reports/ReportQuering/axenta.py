from app.models import CashAxenta
from app.modules import my_time
from app.reports import ReportObject


class AxentaReport(ReportObject):
    name = "axenta"
    headers = ['axenta_id', 'name', 'uid', 'last_time', 'last_pos_time', 'x', 'y']

    def processing(self):
        query = self.db_session.query(CashAxenta).all()
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