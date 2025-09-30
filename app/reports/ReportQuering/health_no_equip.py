from sqlalchemy import func

from app.models import Transport, CashWialon, CashCesar
from app.reports import ReportObject


class HealthNoEquipReport(ReportObject):
    name = "health_no_equip"
    headers = ['uNumber', 'Кол-во wialon', 'Кол-во цезерей']

    def processing(self):
        query = (self.db_session.query(Transport,
                                       self.db_session.query(func.count()).filter(
                                           CashCesar.object_name.like(func.concat('%', Transport.uNumber, '%'))
                                       ).label("cesar_count"),
                                       self.db_session.query(func.count()).filter(
                                           CashWialon.nm.like(func.concat('%', Transport.uNumber, '%'))
                                       ).label("wialon_count"))
                 )
        for row in query:
            transport: Transport
            cesar_count: int
            wialon_count: int

            transport, cesar_count, wialon_count = row
            self.values.append([
                transport.uNumber or '',
                cesar_count or 0,
                wialon_count or 0
            ])