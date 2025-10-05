from sqlalchemy import func

from app.models import Transport, Storage, TransportModel, CashWialon, CashCesar
from app.reports import ReportObject


class MainSummary(ReportObject):
    name = "main_summary"
    headers = ['Тип', 'Регион', 'Склад', '№ Лота', 'Модель', 'Тип подъемника', 'Тип двигателя', 'parser_1c','Cesar Position', 'Wialon']

    def processing(self):
        query = self.db_session.query(Transport, Storage, TransportModel,
            self.db_session.query(func.count()).filter(
                CashCesar.object_name.like(func.concat('%', Transport.uNumber, '%'))
            ).label("cesar_count"),
            self.db_session.query(func.count()).filter(
                CashWialon.nm.like(func.concat('%', Transport.uNumber, '%'))
            ).label("wialon_count")
                ).join(TransportModel, Transport.model_id == TransportModel.id, isouter=True
                ).join(Storage, Transport.storage_id == Storage.ID, isouter=True).all()

        for row in query:
            transport: Transport
            storage: Storage
            transport_model: TransportModel
            cesar_count: int
            wialon_count: int
            transport, storage, transport_model, cesar_count, wialon_count = row

            self.values.append([transport_model.type or '',
                                storage.region or '',
                                storage.name or '',
                                transport.uNumber or '',
                                transport_model.name or '',
                                transport_model.lift_type or '',
                                transport_model.engine or '',
                                transport.parser_1c or 0,
                                cesar_count or 0,
                                wialon_count or 0
                                ])