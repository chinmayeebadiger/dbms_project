from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analysis_is_saved_and_available_in_history():
    response = client.post('/analyze', json={'title': 'API test', 'sql_text': 'DROP TABLE audit_log;'})
    assert response.status_code == 200
    saved = response.json()
    assert saved['migration_id']
    history = client.get('/history').json()['items']
    assert any(item['id'] == saved['migration_id'] for item in history)
    detail = client.get(f"/history/{saved['migration_id']}")
    assert detail.status_code == 200
    assert detail.json()['findings'][0]['operation'] == 'DROP_TABLE'


def test_history_filter_stats_and_graph():
    response = client.post('/analyze', json={'title': 'Graph test', 'sql_text': 'ALTER TABLE users DROP COLUMN email;'})
    saved = response.json()
    assert client.get('/history?risk_level=Critical').status_code == 200
    assert client.get('/stats').json()['critical_count'] >= 1
    graph = client.get(f"/graph/{saved['migration_id']}")
    assert graph.status_code == 200
    assert any(edge['relationship'] == 'HAS_ALTERNATIVE' for edge in graph.json()['edges'])


def test_file_upload_rejects_non_sql_file():
    response = client.post('/analyze-file', files={'file': ('notes.txt', b'DROP TABLE users;')}, data={'title': 'Bad file'})
    assert response.status_code == 415
