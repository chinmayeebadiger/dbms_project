from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

import sqlglot
from sqlglot import exp


@dataclass
class ParsedStatement:
    statement_index: int
    line_number: int
    raw_sql: str
    operation: str | None
    affected_object: str | None
    signals: list[str]
    parse_status: str
    warning: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def split_sql(sql_text: str) -> list[tuple[str, int]]:
    """Split simple migration scripts without losing the first line of each statement."""
    statements: list[tuple[str, int]] = []
    start = 0
    for match in re.finditer(r';', sql_text):
        chunk = sql_text[start:match.start()].strip()
        if chunk:
            first_content = start + (len(sql_text[start:match.start()]) - len(sql_text[start:match.start()].lstrip()))
            line = sql_text.count('\n', 0, first_content) + 1
            statements.append((chunk, line))
        start = match.end()
    tail = sql_text[start:].strip()
    if tail:
        first_content = start + (len(sql_text[start:]) - len(sql_text[start:].lstrip()))
        line = sql_text.count('\n', 0, first_content) + 1
        statements.append((tail, line))
    return statements


def _name(node: Any) -> str | None:
    if node is None:
        return None
    if isinstance(node, exp.Column):
        return node.sql(dialect='postgres')
    if isinstance(node, exp.Table):
        return node.sql(dialect='postgres')
    return getattr(node, 'name', None) or node.sql(dialect='postgres')


def _parse_alter(statement: exp.Alter, raw: str) -> tuple[str | None, str | None, list[str]]:
    table = _name(statement.this)
    actions = statement.args.get('actions') or []
    if not actions:
        return None, table, []
    action = actions[0]
    if isinstance(action, exp.Drop) and str(action.args.get('kind', '')).upper() == 'COLUMN':
        column = _name(action.this)
        if not column:
            return None, table, ['ALTER_TABLE', 'DROP_COLUMN', 'MISSING_COLUMN']
        return 'DROP_COLUMN', f'{table}.{column}', ['ALTER_TABLE', 'DROP_COLUMN']
    if isinstance(action, exp.AlterColumn):
        return 'ALTER_COLUMN_TYPE', f'{table}.{_name(action.this)}', ['ALTER_TABLE', 'ALTER_COLUMN_TYPE']
    if isinstance(action, exp.RenameColumn):
        return 'RENAME_COLUMN', f'{table}.{_name(action.this)}', ['ALTER_TABLE', 'RENAME_COLUMN']
    if isinstance(action, exp.ColumnDef):
        column = f'{table}.{_name(action.this)}'
        has_not_null = any(isinstance(c.args.get('kind'), exp.NotNullColumnConstraint) for c in (action.args.get('constraints') or []))
        if has_not_null:
            return 'ADD_NOT_NULL', column, ['ALTER_TABLE', 'ADD_COLUMN', 'NOT_NULL']
    if isinstance(action, exp.AddConstraint):
        text = action.sql(dialect='postgres').upper()
        if 'FOREIGN KEY' in text:
            return 'ADD_FOREIGN_KEY', table, ['ALTER_TABLE', 'ADD_CONSTRAINT', 'FOREIGN_KEY']
        if 'UNIQUE' in text:
            return 'ADD_UNIQUE', table, ['ALTER_TABLE', 'ADD_CONSTRAINT', 'UNIQUE']
    return None, table, ['ALTER_TABLE', 'UNSUPPORTED_ALTER']


def parse_statement(raw_sql: str, statement_index: int, line_number: int) -> ParsedStatement:
    try:
        statement = sqlglot.parse_one(raw_sql, read='postgres')
    except sqlglot.errors.ParseError as exc:
        return ParsedStatement(statement_index, line_number, raw_sql, None, None, [], 'warning', f'Could not parse SQL: {exc}')

    operation: str | None = None
    affected: str | None = None
    signals: list[str] = []
    if isinstance(statement, exp.Drop):
        kind = str(statement.args.get('kind') or '').upper()
        operation = 'DROP_TABLE' if kind == 'TABLE' else 'DROP_INDEX' if kind == 'INDEX' else None
        affected = _name(statement.this)
        signals = ['DROP', kind] if kind else ['DROP']
    elif isinstance(statement, exp.TruncateTable):
        operation, affected, signals = 'TRUNCATE_TABLE', _name((statement.expressions or [None])[0]), ['TRUNCATE', 'TABLE']
    elif isinstance(statement, exp.Delete):
        affected = _name(statement.this)
        operation = 'DELETE_WITHOUT_WHERE' if statement.args.get('where') is None else None
        signals = ['DELETE'] + (['WITHOUT_WHERE_CLAUSE'] if operation else ['WHERE_CLAUSE'])
    elif isinstance(statement, exp.Update):
        affected = _name(statement.this)
        operation = 'UPDATE_WITHOUT_WHERE' if statement.args.get('where') is None else None
        signals = ['UPDATE'] + (['WITHOUT_WHERE_CLAUSE'] if operation else ['WHERE_CLAUSE'])
    elif isinstance(statement, exp.Alter):
        operation, affected, signals = _parse_alter(statement, raw_sql)
    elif isinstance(statement, exp.Create) and str(statement.args.get('kind') or '').upper() == 'INDEX':
        operation = 'CREATE_INDEX'
        index = statement.this
        affected = _name(index.args.get('table')) if index is not None else None
        signals = ['CREATE', 'INDEX']

    if operation is None:
        return ParsedStatement(statement_index, line_number, raw_sql, None, affected, signals, 'warning', 'Statement is syntactically valid but is outside the supported migration catalog.')
    return ParsedStatement(statement_index, line_number, raw_sql, operation, affected, signals, 'classified')


def parse_migration(sql_text: str) -> list[dict[str, Any]]:
    return [parse_statement(raw, index, line) .as_dict() for index, (raw, line) in enumerate(split_sql(sql_text), start=1)]
