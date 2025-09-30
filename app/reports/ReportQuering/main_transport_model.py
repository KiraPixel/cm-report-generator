from app.models import TransportModel
from app.reports import ReportObject

class MainTransportModelReport(ReportObject):
    name = "main_transport_model"
    headers = ['ID', 'Тип направления', 'Название', 'Тип подъемника', 'Двигатель', 'Страна', 'Тип техники',
               'Бренд', 'Модель']

    def processing(self):
        query = self.db_session.query(
            TransportModel.id,
            TransportModel.type,
            TransportModel.name,
            TransportModel.lift_type,
            TransportModel.engine,
            TransportModel.country,
            TransportModel.machine_type,
            TransportModel.brand,
            TransportModel.model
        ).all()
        for row in query:
            self.values.append([
                row.id or '',
                row.type or '',
                row.name or '',
                row.lift_type or '',
                row.engine or '',
                row.country or '',
                row.machine_type or '',
                row.brand or '',
                row.model or ''
            ])