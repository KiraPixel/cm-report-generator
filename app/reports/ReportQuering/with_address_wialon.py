from sqlalchemy import func

from app.models import CashWialon, Coord
from app.modules import my_time
from app.reports import ReportObject


class WithAddressWialonReport(ReportObject):
    headers = ['wialon_id', 'uNumber', 'uid', 'last_time', 'last_pos_time', 'x', 'y', 'address']
    name = "wialon_with_address"
    localization_name = "Весь транспорт с адресом"
    category = 'wialon'
    heavy_report = True

    def processing(self):
        query = self.db_session.query(
            CashWialon.id,
            CashWialon.nm,
            CashWialon.uid,
            CashWialon.last_time,
            CashWialon.last_pos_time,
            func.min(Coord.address).label('address'),
            func.round(CashWialon.pos_x, 2).label('pos_y'),
            func.round(CashWialon.pos_y, 2).label('pos_x'),
            CashWialon.pos_x.label('orig_pos_y'),
            CashWialon.pos_y.label('orig_pos_x')
        ).join(
            Coord,
            (func.round(Coord.pos_y, 3) == func.round(CashWialon.pos_x, 3)) &
            (func.round(Coord.pos_x, 3) == func.round(CashWialon.pos_y, 3)),
            isouter=True
        ).group_by(
            CashWialon.id,
            CashWialon.nm,
            CashWialon.uid,
            CashWialon.last_time,
            CashWialon.last_pos_time,
            CashWialon.pos_x,
            CashWialon.pos_y
        )

        query_with_address = query.filter(Coord.address.isnot(None))
        query_without_address = query.filter(Coord.address.is_(None))

        total_count = query_with_address.count() + query_without_address.count()
        main_percentage = (query_with_address.count() / total_count) * 100
        self.percentage_completed = (query_with_address.count() / total_count) * 100

        for row in query_with_address:
            self.values.append([
                row.id,
                row.nm or '',
                row.uid or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                my_time.unix_to_moscow_time(row.last_pos_time) or '',
                row.orig_pos_x,
                row.orig_pos_y,
                row.address
            ])

        processed_without_address = 0
        for row in query_without_address:
            processed_without_address += 1
            address = self.get_location(row.orig_pos_x, row.orig_pos_y) if row.pos_y and row.pos_x else ''
            self.values.append([
                row.id,
                row.nm or '',
                row.uid or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                my_time.unix_to_moscow_time(row.last_pos_time) or '',
                row.orig_pos_x,
                row.orig_pos_y,
                address
            ])

            if processed_without_address % 20 == 0:
                if processed_without_address != 0:
                    self.percentage_completed = main_percentage + ((processed_without_address / total_count) * 100)
                    self.update_to_db()

        self.filter_by_transport_access('uNumber')