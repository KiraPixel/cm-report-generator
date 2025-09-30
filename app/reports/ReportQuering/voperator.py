from app.models import Alert, Transport, Storage, TransportModel, AlertTypePresets
from app.modules import my_time
from app.reports import ReportObject


class VOperator(ReportObject):
    name = "voperator"
    headers = ['Дата', '№ лота', 'Тип алерта', 'Информация', 'Комментарии', 'Автор комментария', 'Регион', 'Склад', 'Модель лота',
               'Менеджер', 'Аренда', 'ID пресета', 'Название пресета']

    def processing(self):
        query = (self.db_session.query(Alert, Transport, Storage, TransportModel, AlertTypePresets)
                 .join(Transport, Transport.uNumber == Alert.uNumber)
                 .join(Storage, Transport.storage_id == Storage.ID)
                 .join(TransportModel, Transport.model_id == TransportModel.id)
                 .join(AlertTypePresets, AlertTypePresets.id == Transport.alert_preset)
                 .filter(Alert.status == 0).all())

        for row in query:
            alert: Alert
            transport: Transport
            storage: Storage
            transport_model: TransportModel
            alert_type: AlertTypePresets

            alert, transport, storage, transport_model, alert_type = row
            self.values.append([
                my_time.unix_to_moscow_time(alert.date) or '',
                alert.uNumber or '',
                alert.type or '',
                alert.data or '',
                alert.comment or '',
                alert.comment_editor or '',
                storage.region or '',
                storage.name or '',
                transport_model.name or '',
                transport.manager or '',
                transport.customer or '',
                alert_type.id or '',
                alert_type.preset_name or '',
            ])