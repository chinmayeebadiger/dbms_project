from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import delete, func, insert, select

from ..db import detected_risks, engine, kg_edges, kg_nodes, migrations


def _iso(value):
    return value.isoformat() if hasattr(value, 'isoformat') else str(value)


def _analysis_from_row(connection, row) -> dict:
    migration_id = row.id
    findings = [dict(item) for item in connection.execute(select(detected_risks).where(detected_risks.c.migration_id == migration_id)).mappings().all()]
    node_rows = connection.execute(select(kg_nodes).where(kg_nodes.c.migration_id == migration_id)).mappings().all()
    node_map = {node['id']: {'id': f"{node['node_key']}", 'node_type': node['node_type'], 'label': node['label']} for node in node_rows}
    edges = []
    for edge in connection.execute(select(kg_edges).where(kg_edges.c.migration_id == migration_id)).mappings().all():
        source = node_map.get(edge['source_node_id'], {}).get('id', str(edge['source_node_id']))
        target = node_map.get(edge['target_node_id'], {}).get('id', str(edge['target_node_id']))
        edges.append({'id': f'{source}-{edge["relationship"]}-{target}', 'source': source, 'target': target, 'relationship': edge['relationship']})
    return {
        'migration_id': migration_id,
        'title': row.title,
        'sql_text': row.sql_text,
        'overall_score': float(row.risk_score),
        'risk_level': row.risk_level,
        'warnings': row.warnings or [],
        'created_at': _iso(row.created_at),
        'statements': row.statements or [],
        'findings': findings,
        'graph': {'nodes': list(node_map.values()), 'edges': edges},
    }


def save_analysis(title: str, sql_text: str, result: dict) -> dict:
    migration_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(insert(migrations).values(
            id=migration_id, title=title or 'Untitled migration', sql_text=sql_text,
            risk_score=result['overall_score'], risk_level=result['risk_level'],
            statements=result.get('statements', []), warnings=result.get('warnings', []), created_at=created_at,
        ))
        for finding in result.get('findings', []):
            connection.execute(insert(detected_risks).values(
                migration_id=migration_id, operation=finding['operation'], affected_object=finding.get('affected_object'),
                risk_type=finding['risk_type'], severity=finding['severity'], explanation=finding['explanation'],
                impact=finding['impact'], alternative=finding['alternative'], line_number=finding['line_number'],
            ))
        node_ids = {}
        for node in result.get('graph', {}).get('nodes', []):
            node_key = node['id']
            node_id = connection.execute(insert(kg_nodes).values(
                migration_id=migration_id, node_type=node['node_type'], node_key=node_key, label=node['label'],
            ).returning(kg_nodes.c.id)).scalar_one()
            node_ids[node_key] = node_id
        for edge in result.get('graph', {}).get('edges', []):
            if edge['source'] in node_ids and edge['target'] in node_ids:
                connection.execute(insert(kg_edges).values(
                    migration_id=migration_id, source_node_id=node_ids[edge['source']], relationship=edge['relationship'], target_node_id=node_ids[edge['target']],
                ))
    saved = dict(result)
    saved.update({'migration_id': migration_id, 'title': title or 'Untitled migration', 'sql_text': sql_text, 'created_at': created_at.isoformat()})
    return saved


def list_history(risk_level: str | None = None) -> list[dict]:
    with engine.connect() as connection:
        query = select(migrations).order_by(migrations.c.created_at.desc())
        if risk_level:
            query = query.where(func.lower(migrations.c.risk_level) == risk_level.lower())
        rows = connection.execute(query).mappings().all()
        result = []
        for row in rows:
            count = connection.execute(select(func.count()).select_from(detected_risks).where(detected_risks.c.migration_id == row['id'])).scalar_one()
            result.append({'id': row['id'], 'title': row['title'], 'risk_level': row['risk_level'], 'risk_score': float(row['risk_score']), 'created_at': _iso(row['created_at']), 'findings_count': count})
        return result


def get_analysis(migration_id: str) -> dict | None:
    with engine.connect() as connection:
        row = connection.execute(select(migrations).where(migrations.c.id == migration_id)).mappings().first()
        if row is None:
            return None
        class Row:
            pass
        obj = Row()
        for key, value in row.items():
            setattr(obj, key, value)
        return _analysis_from_row(connection, obj)


def stats() -> dict:
    with engine.connect() as connection:
        count = connection.execute(select(func.count()).select_from(migrations)).scalar_one()
        average = connection.execute(select(func.avg(migrations.c.risk_score))).scalar_one()
        critical = connection.execute(select(func.count()).select_from(migrations).where(func.lower(migrations.c.risk_level) == 'critical')).scalar_one()
        return {'analyses_count': count, 'average_score': round(float(average), 1) if average is not None else 0, 'critical_count': critical}


def clear_history() -> None:
    with engine.begin() as connection:
        connection.execute(delete(kg_edges))
        connection.execute(delete(kg_nodes))
        connection.execute(delete(detected_risks))
        connection.execute(delete(migrations))
