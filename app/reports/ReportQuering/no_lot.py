from app.models import Transport, CashCesar, CashWialon
from app.reports import ReportObject


class HealthNoLotReport(ReportObject):
    headers = ['Тип', 'Имя в системе', 'WialonID/PIN']
    name = "health_no_lot"
    localization_name = "Оборудование без лота"
    category = 'health'

    def processing(self):
        transport_numbers = {t.uNumber for t in self.db_session.query(Transport).all()}
        for cesar in self.db_session.query(CashCesar).all():
            if not any(transport_number in cesar.object_name for transport_number in transport_numbers):
                self.values.append(['Cesar', cesar.object_name or '', cesar.pin or ''])
        for wialon in self.db_session.query(CashWialon).all():
            if not any(transport_number in wialon.nm for transport_number in transport_numbers):
                self.values.append(['Wialon', wialon.nm or '', wialon.uid or ''])

        self.filter_by_transport_access('Имя в системе')