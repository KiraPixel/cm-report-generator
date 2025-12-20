from app.models import Transport, TransportModel, Storage
from app.reports import ReportObject


class TransportReport(ReportObject):
    headers = ['ID', 'ID склада', 'Название склада', 'ID модели', 'Название модели', '№ Лота', 'Год выпуска', 'VIN', 'X', 'Y', 'Клиент',
               'Контакт клиента', 'Менеджер', 'parser_1c']
    name = "all_transport"
    category = 'reports_operator'
    localization_name = "Все транспортные средства"

    def processing(self):
        query = (self.db_session.query(Transport, TransportModel, Storage)
                 .join(TransportModel, TransportModel.id == Transport.model_id)
                 .join(Storage, Storage.ID == Transport.storage_id)
                 .all())
        for row in query:
            transport: Transport
            storage: Storage
            transport_model: TransportModel
            transport, transport_model, storage = row
            self.values.append([
                transport.id or '',
                transport.storage_id or '',
                storage.name or '',
                transport.model_id or '',
                transport_model.name or '',
                transport.uNumber or '',
                transport.manufacture_year or '',
                transport.vin or '',
                transport.x or '',
                transport.y or '',
                transport.customer or '',
                transport.customer_contact or '',
                transport.manager or '',
                transport.parser_1c or 0
            ])

        self.filter_by_transport_access('№ Лота')
