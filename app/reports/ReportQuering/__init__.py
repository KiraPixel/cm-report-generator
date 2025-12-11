from app.reports import ReportObject
from .axenta import AxentaReport
from .cesar import CesarReport
from .cesar_offline import CesarOfflineReport
from .with_address_axenta import WithAddressAxentaReport
from .with_address_cesar import WithAddressCesarReport
from .custom_transport_transfer import CustomTransportTransferReport
from .health_coordinates import HealthCoordinates
from .health_no_equip import HealthNoEquipReport
from .health_no_lot import HealthNoLotReport
from .main_storage import MainStorageReport
from .main_summary import MainSummary
from .main_transport import MainTransportReport
from .voperator import VOperator
from .wialon import WialonReport
from .wialon_offline import WialonOfflineReport
from .with_address_wialon import WithAddressWialonReport
from .main_transport_model import MainTransportModelReport


report_classes = {
        'wialon': WialonReport,
        'wialon_offline': WialonOfflineReport,
        'cesar': CesarReport,
        'cesar_offline': CesarOfflineReport,
        'axenta': AxentaReport,
        'axenta_offline': WithAddressCesarReport,
        'with_address_cesar': WithAddressCesarReport,
        'with_address_wialon': WithAddressWialonReport,
        'with_address_axenta': WithAddressAxentaReport,
        'health_coordinates': HealthCoordinates,
        'health_no_equip': HealthNoEquipReport,
        'health_no_lot': HealthNoLotReport,
        'voperator': VOperator,
        'main_summary': MainSummary,
        'main_transport': MainTransportReport,
        'main_transport_model': MainTransportModelReport,
        'main_storage': MainStorageReport,
        'custom_transport_transfer': CustomTransportTransferReport
    }

def get_report_class(report_name: str) -> ReportObject | None:
    """
    Возвращает класс отчета по его названию или None, если отчет не найден.

    Args:
        report_name (str): Название отчета (например, 'wialon', 'cesar', 'main_summary').

    Returns:
        ReportObject: Класс отчета или None.
    """
    return report_classes.get(report_name)


def get_all_report_classes_info() -> list[dict]:
    """
    Возвращает список всех доступных классов отчетов с базовой информацией.

    Returns:
        list[dict]: Список словарей с инфой о каждом классе отчета.
    """
    report_list = []
    for key, cls in report_classes.items():
        info = {
            "report_name": key,
            "localization_name": getattr(cls, "localization_name", None),
            "headers": getattr(cls, "headers", None),
            "isRoutineReport": bool(getattr(cls, "isRoutineReport", False)),
            "heavy_report": bool(getattr(cls, "heavy_report", False)),
            "configuration": getattr(cls, "configuration", None),
        }
        report_list.append(info)
    return report_list

