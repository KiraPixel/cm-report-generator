from sqlalchemy import func

from app.models import Transport,  CashWialon
from app.modules import coord_math
from app.reports import ReportObject


class HealthCoordinates(ReportObject):
    name = "health_coordinates"
    headers = ['Номер лота', 'Блок в Wialon', 'Дистанция до объекта']

    def processing(self):
        query = self.db_session.query(Transport, CashWialon).join(CashWialon, CashWialon.nm.like(func.concat('%', Transport.uNumber, '%'))).filter(Transport.x != 0).all()
        for row in query:
            transport, cash_wialon = row
            if transport.x == 0:
                return None
            wialon_pos = (cash_wialon.pos_y, cash_wialon.pos_x)
            work_pos = (transport.x, transport.y)
            delta = coord_math.calculate_distance(wialon_pos, work_pos) if cash_wialon.pos_y != 0 else None
            self.values.append([transport.uNumber or '', cash_wialon.uid or '', delta or ''])