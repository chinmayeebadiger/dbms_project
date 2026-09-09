from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .services.analyzer import analyze_sql
from .services.store import get_analysis, list_history, save_analysis, stats
from .db import initialize_database

initialize_database()

app = FastAPI(title='Database Migration Safety Platform', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174'], allow_methods=['*'], allow_headers=['*'])


class AnalyzeRequest(BaseModel):
    title: str = Field(default='Untitled migration', max_length=120)
    sql_text: str = Field(min_length=1, max_length=1_000_000)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


def _response(title: str, sql_text: str) -> dict:
    result = analyze_sql(sql_text)
    return save_analysis(title, sql_text, result)


@app.post('/analyze')
def analyze(request: AnalyzeRequest) -> dict:
    return _response(request.title, request.sql_text)


@app.post('/analyze-file')
async def analyze_file(file: UploadFile = File(...), title: str = Form('Untitled migration')) -> dict:
    if not file.filename or not file.filename.lower().endswith('.sql'):
        raise HTTPException(status_code=415, detail='Only .sql files are supported.')
    payload = await file.read()
    if len(payload) > 1_000_000:
        raise HTTPException(status_code=413, detail='SQL files must be 1 MB or smaller.')
    try:
        sql_text = payload.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail='The SQL file must be UTF-8 encoded.') from exc
    if not sql_text.strip():
        raise HTTPException(status_code=422, detail='SQL input cannot be empty.')
    return _response(title, sql_text)


@app.get('/history')
def history(risk_level: str | None = Query(default=None)) -> dict:
    return {'items': list_history(risk_level)}


@app.get('/history/{migration_id}')
def history_item(migration_id: str) -> dict:
    item = get_analysis(migration_id)
    if item is None:
        raise HTTPException(status_code=404, detail='Analysis not found.')
    return item


@app.get('/stats')
def dashboard_stats() -> dict:
    return stats()


@app.get('/graph/{migration_id}')
def graph(migration_id: str) -> dict:
    item = get_analysis(migration_id)
    if item is None:
        raise HTTPException(status_code=404, detail='Analysis not found.')
    return item['graph']
