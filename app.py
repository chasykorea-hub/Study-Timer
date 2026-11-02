from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "study_timer.sqlite3"
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def connect_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS study_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            study_date TEXT NOT NULL,
            started_at TEXT NOT NULL,
            subject TEXT NOT NULL,
            minutes INTEGER NOT NULL CHECK(minutes > 0)
        )""")
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Study Timer", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class RecordIn(BaseModel):
    user_name: str = Field(min_length=1, max_length=60)
    subject: str = Field(min_length=1, max_length=100)
    started_at: Optional[datetime] = None
    minutes: int = Field(default=25, ge=1, le=240)


def clean(value: str, label: str):
    value = value.strip()
    if not value:
        raise HTTPException(400, f"{label}을(를) 입력해 주세요.")
    return value


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/records", status_code=201)
async def create_record(payload: RecordIn):
    user_name = clean(payload.user_name, "사용자 이름")
    subject = clean(payload.subject, "과목")
    started = payload.started_at or datetime.now().astimezone()
    started_text = started.isoformat(timespec="seconds")
    with connect_db() as db:
        cursor = db.execute("INSERT INTO study_records(user_name, study_date, started_at, subject, minutes) VALUES (?, ?, ?, ?, ?)",
                            (user_name, started.date().isoformat(), started_text, subject, payload.minutes))
        db.commit()
        record_id = cursor.lastrowid
    return {"id": record_id, "message": "집중 세션 기록이 저장되었습니다.", "minutes": payload.minutes}


@app.get("/api/stats")
async def stats(user_name: str):
    user_name = clean(user_name, "사용자 이름")
    today = date.today()
    start = today - timedelta(days=6)
    with connect_db() as db:
        rows = db.execute("SELECT study_date, subject, SUM(minutes) AS minutes FROM study_records WHERE user_name = ? AND study_date BETWEEN ? AND ? GROUP BY study_date, subject ORDER BY study_date", (user_name, start.isoformat(), today.isoformat())).fetchall()
    daily = { (today - timedelta(days=i)).isoformat(): 0 for i in range(6, -1, -1) }
    subjects = {}
    for row in rows:
        daily[row["study_date"]] += row["minutes"]
        if row["study_date"] == today.isoformat():
            subjects[row["subject"]] = subjects.get(row["subject"], 0) + row["minutes"]
    return {"today": [{"subject": k, "minutes": v} for k, v in sorted(subjects.items())], "last_7_days": [{"date": k, "minutes": v} for k, v in daily.items()]}
