from app.models import CashCesar
from app.modules import my_time
from app.reports import ReportObject


class CesarReport(ReportObject):
    name = "cesar"
    headers = ['cesar_id', 'uNumber', 'PIN', 'created', 'last_online', 'x', 'y']

    def processing(self):
        query = self.db_session.query(CashCesar).all()
        for row in query:
            self.values.append([
                row.unit_id or '',
                row.object_name or '',
                row.pin or '',
                my_time.unix_to_moscow_time(row.created_at) or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                row.pos_x or '',
                row.pos_y or ''
            ])