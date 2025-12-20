import os

from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import worker
from app.reports import ReportObject
from app.reports.ReportQuering import get_report_class, get_all_report_classes_info
from app.reports.category import REPORT_CATEGORIES

app = FastAPI(title="CM Report Generator", docs_url="/docs")

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///default.db')
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

def get_session() -> sessionmaker:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

class GenerateReportRequest(BaseModel):
    report_name: str
    username: str
    parameters: Optional[Dict[str, Any]] = None
    send_to_mail: bool = False

class ReportTypeInfo(BaseModel):
    report_name: str
    localization_name: Optional[str] = None
    category: str
    headers: Optional[List[str]] = None
    isRoutineReport: bool = False
    heavy_report: bool = False
    configuration: Optional[dict] = None

class ReportCategory(BaseModel):
    id: str
    name: str
    localization_name: str
    need_access: str
    position: int

class ReportModel(BaseModel):
    id: int
    name: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[int] = None
    updated_date: Optional[int] = None
    end_date: Optional[int] = None
    isValid: Optional[bool] = None
    isSuccess: Optional[bool] = None
    headers: Optional[List[str]] = None
    error: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


@app.get("/report-list", response_model=List[ReportTypeInfo])
def list_report_types():
    """Возвращает список доступных типов отчётов с базовой информацией"""
    return get_all_report_classes_info()

@app.get("/report-categories", response_model=List[ReportCategory])
def get_report_categories():
    """Возвращает список категорий отчетов"""
    categories = [
        ReportCategory(
            id=key,
            name=value["name"],
            localization_name=value["localization_name"],
            need_access=value["need_access"],
            position=value["position"]
        )
        for key, value in REPORT_CATEGORIES.items()
    ]
    return sorted(categories, key=lambda x: x.position)


@app.get("/report-info/{report_id}", response_model=ReportModel)
def get_report_info(report_id: str=None):
    try:
        report_id = int(report_id)
    except ValueError as e:
        raise HTTPException(400 , detail=str(e))

    session = get_session()

    report = ReportObject(db_session=session(), report_id=int(report_id), username=None)

    if not report.isSuccess:
        raise HTTPException(status_code=500, detail=report.error)

    report.get_from_db() # обновление на случай старых отчетов todo прогнать старые отчеты
    info = ReportModel(
        id=report.id,
        name=report.name,
        owner=report.owner_name,
        status=report.status,
        start_date=report.start_date,
        updated_date=report.updated_date,
        end_date=report.end_date,
        isValid=report.isValid,
        isSuccess=report.isSuccess,
        headers=report.headers,
        error=report.error,
        parameters=report.parameters,
    )

    return info


@app.post("/generate-report", response_model=dict)
def generate_report(request: GenerateReportRequest, background_tasks: BackgroundTasks):
    session = get_session()
    try:
        report_class = get_report_class(request.report_name)
        if report_class is None:
            raise HTTPException(400, detail="Invalid report report_name")

        if report_class.configuration is not None:
            if request.parameters is None or not request.parameters:
                raise HTTPException(400, detail="Invalid parameters")

        if report_class.heavy_report or request.send_to_mail:
            background_tasks.add_task(
                worker.start,
                session=session(),
                reportQuery=None,
                report=report_class,
                username=request.username,
                parameters=request.parameters,
                need_send_to_mail=True,
                is_api_request=True,
            )
            return {"status": "in_progress", "message": "Отчёт будет отправлен на почту"}


        report_instance = report_class(session(), report_id=None, username=request.username, parameters=request.parameters)

        if not report_instance.isValid or not report_instance.isSuccess:
            error_msg = report_instance.error or "Ошибка при генерации отчета"
            raise HTTPException(500, detail=error_msg)

        report_instance.get_from_db()
        json_result = report_instance.to_json()
        return json_result

    except Exception as e:
        raise HTTPException(500, detail=str(e))

    finally:
        session().close()