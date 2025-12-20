from app.models import CashCesar, Coord
from app.modules import my_time
from app.reports import ReportObject
from sqlalchemy import func

class WithAddressCesarReport(ReportObject):
    headers = ['cesar_id', 'uNumber', 'PIN', 'last_online', 'address', 'x', 'y']
    name = "cesar_with_address"
    localization_name = "Весь транспорт с адресом"
    category = 'cesar'
    heavy_report = True

    def processing(self):
        query = self.db_session.query(
            CashCesar.unit_id,
            CashCesar.object_name,
            CashCesar.pin,
            CashCesar.last_time,
            func.min(Coord.address).label('address'),
            func.round(CashCesar.pos_x, 2).label('pos_x'),
            func.round(CashCesar.pos_y, 2).label('pos_y'),
            CashCesar.pos_x.label('orig_pos_x'),
            CashCesar.pos_y.label('orig_pos_y')
        ).join(
            Coord,
            (func.round(Coord.pos_y, 3) == func.round(CashCesar.pos_y, 3)) &
            (func.round(Coord.pos_x, 3) == func.round(CashCesar.pos_x, 3)),
            isouter=True
        ).group_by(
            CashCesar.unit_id,
            CashCesar.object_name,
            CashCesar.pin,
            CashCesar.last_time,
            CashCesar.pos_x,
            CashCesar.pos_y
        )

        query_with_address = query.filter(Coord.address.isnot(None))
        query_without_address = query.filter(Coord.address.is_(None))

        total_count = query_with_address.count() + query_without_address.count()
        main_percentage = (query_with_address.count() / total_count) * 100
        self.percentage_completed = (query_with_address.count() / total_count) * 100

        for row in query_with_address:
            self.values.append([
                row.unit_id or '',
                row.object_name or '',
                row.pin or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                row.address,
                row.pos_x,
                row.pos_y,
            ])

        self.update_to_db()
        processed_without_address = 0
        for row in query_without_address:
            processed_without_address += 1
            address = self.get_location(row.orig_pos_x, row.orig_pos_y) if row.pos_y and row.pos_x else ''
            self.values.append([
                row.unit_id or '',
                row.object_name or '',
                row.pin or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                address,
                row.pos_x,
                row.pos_y,
            ])

            if processed_without_address % 20 == 0:
                self.percentage_completed = main_percentage + ((processed_without_address / total_count) * 100)
                self.update_to_db()
        self.filter_by_transport_access('uNumber')