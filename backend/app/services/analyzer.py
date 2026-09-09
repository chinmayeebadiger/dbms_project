from __future__ import annotations

from typing import Any

from .parser import parse_migration
from .risk_catalog import RISK_CATALOG, SEVERITY_SCORE


def _graph_for(finding: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    nodes = []
    edges = []
    operation = finding['operation']
    object_label = finding['affected_object'] or 'UNKNOWN_OBJECT'
    nodes.append({'id': f'operation:{operation}', 'node_type': 'Operation', 'label': operation})
    object_id = f'object:{object_label}'
    nodes.append({'id': object_id, 'node_type': 'Database Object', 'label': object_label})
    for relationship, target in finding['relationships']:
        target_type = {'AFFECTS': 'Database Object', 'MAY_CAUSE': 'Risk', 'HAS_SEVERITY': 'Severity', 'HAS_ALTERNATIVE': 'Safer Alternative'}.get(relationship, 'Condition')
        target_id = object_id if relationship == 'AFFECTS' else f'{target_type.lower().replace(" ", "-")}:{target}'
        if relationship == 'MAY_CAUSE':
            target_id = f'risk:{finding["risk_type"]}'
            target = finding['risk_type']
        nodes.append({'id': target_id, 'node_type': target_type, 'label': target})
        source_id = f'operation:{operation}' if relationship in {'AFFECTS', 'MAY_CAUSE'} else f'risk:{finding["risk_type"]}'
        if relationship == 'HAS_SEVERITY':
            source_id = f'risk:{finding["risk_type"]}'
        if relationship == 'HAS_ALTERNATIVE':
            source_id = f'risk:{finding["risk_type"]}'
        edges.append({'id': f'{source_id}-{relationship}-{target_id}', 'source': source_id, 'target': target_id, 'relationship': relationship})
    # Normalize risk node and connect the operation to it before deduplication.
    risk_id = f'risk:{finding["risk_type"]}'
    nodes.append({'id': risk_id, 'node_type': 'Risk', 'label': finding['risk_type']})
    edges.append({'id': f'operation:{operation}-MAY_CAUSE-{risk_id}', 'source': f'operation:{operation}', 'target': risk_id, 'relationship': 'MAY_CAUSE'})
    unique_nodes = {node['id']: node for node in nodes}
    unique_edges = {edge['id']: edge for edge in edges}
    return {'nodes': list(unique_nodes.values()), 'edges': list(unique_edges.values())}


def analyze_sql(sql_text: str) -> dict[str, Any]:
    statements = parse_migration(sql_text)
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for parsed in statements:
        if parsed['parse_status'] != 'classified':
            warnings.append({'line_number': parsed['line_number'], 'message': parsed['warning']})
            continue
        rule = RISK_CATALOG[parsed['operation']]
        finding = {
            'operation': parsed['operation'],
            'affected_object': parsed['affected_object'],
            'risk_type': rule['risk_type'],
            'severity': rule['severity'],
            'explanation': rule['explanation'],
            'impact': rule['impact'],
            'alternative': rule['alternative'],
            'line_number': parsed['line_number'],
            'relationships': rule['relationships'],
        }
        findings.append(finding)
    deduped = list({(f['operation'], f['affected_object'], f['line_number']): f for f in findings}.values())
    scores = [SEVERITY_SCORE[f['severity']] for f in deduped]
    max_score = max(scores, default=0)
    remaining = scores.copy()
    if remaining:
        remaining.remove(max_score)
    score = min(100, round(max_score + 0.10 * sum(remaining), 2))
    level = 'Low' if score <= 25 else 'Medium' if score <= 50 else 'High' if score <= 75 else 'Critical'
    graph = {'nodes': [], 'edges': []}
    for finding in deduped:
        part = _graph_for(finding)
        graph['nodes'].extend(part['nodes']); graph['edges'].extend(part['edges'])
    graph['nodes'] = list({node['id']: node for node in graph['nodes']}.values())
    graph['edges'] = list({edge['id']: edge for edge in graph['edges']}.values())
    for finding in deduped:
        finding.pop('relationships', None)
    return {'overall_score': score, 'risk_level': level, 'statements': statements, 'findings': deduped, 'warnings': warnings, 'graph': graph}
