from app.reports import ReportObject


class ReportTemplate(ReportObject):
    name = "report_template"
    headers = ['ID', 'Ошибка']

    def processing(self):
        if self.parameters is None:
            raise ValueError("Параметры отчёта не предоставлены")

        print(f"Обработка отчёта '{self.name}' для владельца {self.owner_name}")

        self.values = ['0', 'error this is tempalte']
        self.finish_processing(True, '')