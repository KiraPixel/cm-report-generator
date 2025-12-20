from app.models import TransportModel
from app.reports import ReportObject

class TransportModelReport(ReportObject):
    headers = [
        'ID',
        'Тип направления',
        'Название',
        'Тип подъемника',
        'Высота подъемника',
        'Двигатель',
        'Страна',
        'Тип техники',
        'Бренд',
        'Модель'
   ]
    name = "all_transport_model"
    category = 'reports_operator'
    localization_name = "Все модели ТС"

    def processing(self):
        query = self.db_session.query(
            TransportModel.id,
            TransportModel.type,
            TransportModel.name,
            TransportModel.lift_type,
            TransportModel.lifting_height,
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
                row.lifting_height or '',
                row.engine or '',
                row.country or '',
                row.machine_type or '',
                row.brand or '',
                row.model or ''
            ])