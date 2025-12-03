from sqlalchemy import func

from app.models import CashAxenta, Coord
from app.modules import my_time
from app.reports import ReportObject


class WithAddressAxentaReport(ReportObject):
    name = "axenta_with_address"
    headers = ['axenta_id', 'uNumber', 'uid', 'last_time', 'last_pos_time', 'x', 'y', 'address']
    heavy_report = True

    def processing(self):
        query = self.db_session.query(
            CashAxenta.id,
            CashAxenta.nm,
            CashAxenta.uid,
            CashAxenta.last_time,
            CashAxenta.last_pos_time,
            CashAxenta.pos_x,
            CashAxenta.pos_y,
            func.min(Coord.address).label('address')
        ).join(
            Coord,
            (func.round(Coord.pos_x, 3) == func.round(CashAxenta.pos_x, 3)) &
            (func.round(Coord.pos_y, 3) == func.round(CashAxenta.pos_y, 3)),
            isouter=True
        ).group_by(
            CashAxenta.id,
            CashAxenta.nm,
            CashAxenta.uid,
            CashAxenta.last_time,
            CashAxenta.last_pos_time,
            CashAxenta.pos_x,
            CashAxenta.pos_y
        )

        query_with_address = query.having(func.min(Coord.address).isnot(None))
        query_without_address = query.having(func.min(Coord.address).is_(None))

        with_count = query_with_address.count()
        without_count = query_without_address.count()
        total_count = with_count + without_count

        if total_count == 0:
            self.percentage_completed = 100
            return

        main_percentage = (with_count / total_count) * 100
        self.percentage_completed = main_percentage
        # self.update_to_db()  # можно добавить, если хочется обновить после первой части

        # ─── Объекты, у которых уже есть адрес ───
        for row in query_with_address:
            self.values.append([
                row.id,
                row.nm or '',
                row.uid or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                my_time.unix_to_moscow_time(row.last_pos_time) or '',
                row.pos_x,
                row.pos_y,
                row.address
            ])

        # ─── Объекты без адреса — получаем через геокодер ───
        processed_without_address = 0
        for row in query_without_address:
            processed_without_address += 1

            address = (
                self.get_location(row.pos_x, row.pos_y)
                if row.pos_x and row.pos_y else ''
            )

            self.values.append([
                row.id,
                row.nm or '',
                row.uid or '',
                my_time.unix_to_moscow_time(row.last_time) or '',
                my_time.unix_to_moscow_time(row.last_pos_time) or '',
                row.pos_x,
                row.pos_y,
                address
            ])

            if processed_without_address % 20 == 0:
                self.percentage_completed = main_percentage + (processed_without_address / total_count) * 100
                self.update_to_db()

        # Финальное обновление прогресса
        self.percentage_completed = 100
        self.update_to_db()