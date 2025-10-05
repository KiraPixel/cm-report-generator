from sqlalchemy.orm import Session

from app.models import Reports
from app.reports import ReportObject


def start(reportQuery: Reports, report: ReportObject, session: Session, report_id=None, username=None, parameters=None, need_send_to_mail=False):
    if report_id is None:
        report_id = reportQuery.id
        if report_id is None:
            return False
    if username is None:
        username = reportQuery.username
        if username is None:
            return False
    if parameters is None:
        parameters = report.parameters

    report_instance = report(session, report_id=report_id, username=username, parameters=parameters)

    if need_send_to_mail:
        report_instance.send_to_mail()

    session.close()

    return True



