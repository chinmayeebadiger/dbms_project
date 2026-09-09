from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .services.analyzer import analyze_sql

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
    result['migration_id'] = None
    result['title'] = title or 'Untitled migration'
    return result


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
