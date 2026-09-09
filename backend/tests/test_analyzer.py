from app.services.analyzer import analyze_sql
from app.services.parser import parse_migration


def test_parser_classifies_catalog_examples():
    sql = '''DROP TABLE users;
ALTER TABLE customers DROP COLUMN email;
TRUNCATE TABLE sessions;
DELETE FROM users;
UPDATE users SET active = false;
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;
ALTER TABLE users RENAME COLUMN name TO full_name;
ALTER TABLE users ADD COLUMN phone TEXT NOT NULL;
ALTER TABLE users ADD CONSTRAINT uq UNIQUE (email);
ALTER TABLE orders ADD CONSTRAINT fk FOREIGN KEY (user_id) REFERENCES users(id);
CREATE INDEX idx_users_email ON users(email);
DROP INDEX idx_users_email;'''
    parsed = parse_migration(sql)
    assert [item['operation'] for item in parsed] == [
        'DROP_TABLE', 'DROP_COLUMN', 'TRUNCATE_TABLE', 'DELETE_WITHOUT_WHERE',
        'UPDATE_WITHOUT_WHERE', 'ALTER_COLUMN_TYPE', 'RENAME_COLUMN', 'ADD_NOT_NULL',
        'ADD_UNIQUE', 'ADD_FOREIGN_KEY', 'CREATE_INDEX', 'DROP_INDEX',
    ]
    assert [item['line_number'] for item in parsed] == list(range(1, 13))


def test_where_clause_is_not_mass_update():
    parsed = parse_migration('UPDATE users SET active = false WHERE id = 1;')
    assert parsed[0]['operation'] is None
    assert parsed[0]['parse_status'] == 'warning'


def test_malformed_sql_becomes_warning():
    parsed = parse_migration('ALTER TABLE users DROP COLUMN;')
    assert parsed[0]['parse_status'] == 'warning'
    assert parsed[0]['warning']


def test_analyzer_returns_critical_finding_and_graph():
    result = analyze_sql('ALTER TABLE customers DROP COLUMN email;\nUPDATE customers SET active = false;')
    assert result['overall_score'] == 96.5
    assert result['risk_level'] == 'Critical'
    assert len(result['findings']) == 2
    assert any(node['node_type'] == 'Safer Alternative' for node in result['graph']['nodes'])
    assert any(edge['relationship'] == 'HAS_SEVERITY' for edge in result['graph']['edges'])


def test_safe_or_supported_statement_warning_is_explicit():
    result = analyze_sql('ALTER TABLE users ADD COLUMN nickname TEXT;')
    assert result['findings'] == []
    assert result['warnings'][0]['line_number'] == 1
