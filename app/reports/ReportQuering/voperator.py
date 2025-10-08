from app.models import Alert, Transport, Storage, TransportModel, AlertTypePresets
from app.modules import my_time
from app.reports import ReportObject


class VOperator(ReportObject):
    name = "voperator"
    headers = ['Дата', '№ лота', 'Тип алерта', 'Информация', 'Комментарии', 'Автор комментария', 'Регион', 'Склад', 'Модель лота',
               'Менеджер', 'Аренда', 'ID пресета', 'Название пресета']

    def processing(self):
        query = (self.db_session.query(Alert, Transport, Storage, TransportModel, AlertTypePresets)
                 .outerjoin(Transport, Transport.uNumber == Alert.uNumber)
                 .outerjoin(Storage, Transport.storage_id == Storage.ID)
                 .outerjoin(TransportModel, Transport.model_id == TransportModel.id)
                 .outerjoin(AlertTypePresets, AlertTypePresets.id == Transport.alert_preset)
                 .filter(Alert.status == 0).all())

        for row in query:
            alert: Alert
            transport: Transport
            storage: Storage
            transport_model: TransportModel
            alert_type: AlertTypePresets

            alert, transport, storage, transport_model, alert_type = row
            self.values.append([
                my_time.unix_to_moscow_time(alert.date) if alert and alert.date else '',
                alert.uNumber if alert else '',
                alert.type if alert else '',
                alert.data if alert else '',
                alert.comment if alert else '',
                alert.comment_editor if alert else '',
                storage.region if storage else '',
                storage.name if storage else '',
                transport_model.name if transport_model else '',
                transport.manager if transport else '',
                transport.customer if transport else '',
                alert_type.id if alert_type else '',
                alert_type.preset_name if alert_type else '',
            ])