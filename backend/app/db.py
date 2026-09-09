from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sqlalchemy import Column, JSON, DateTime, ForeignKey, Integer, MetaData, Numeric, String, Table, Text, UniqueConstraint, create_engine, select
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "migration_safety.db"}')
engine: Engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
metadata = MetaData()

migrations = Table('migrations', metadata,
    Column('id', String(36), primary_key=True),
    Column('title', String(120), nullable=False),
    Column('sql_text', Text, nullable=False),
    Column('risk_score', Numeric(5, 2), nullable=False),
    Column('risk_level', String(20), nullable=False),
    Column('statements', JSON, nullable=False, default=list),
    Column('warnings', JSON, nullable=False, default=list),
    Column('created_at', DateTime(timezone=True), nullable=False),
)
detected_risks = Table('detected_risks', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('migration_id', String(36), ForeignKey('migrations.id', ondelete='CASCADE'), nullable=False),
    Column('operation', String(80), nullable=False),
    Column('affected_object', String(255)),
    Column('risk_type', String(100), nullable=False),
    Column('severity', String(20), nullable=False),
    Column('explanation', Text, nullable=False),
    Column('impact', Text, nullable=False),
    Column('alternative', Text, nullable=False),
    Column('line_number', Integer, nullable=False),
)
kg_nodes = Table('kg_nodes', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('migration_id', String(36), ForeignKey('migrations.id', ondelete='CASCADE'), nullable=False),
    Column('node_type', String(80), nullable=False),
    Column('node_key', String(255), nullable=False),
    Column('label', String(255), nullable=False),
    UniqueConstraint('migration_id', 'node_key'),
)
kg_edges = Table('kg_edges', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('migration_id', String(36), ForeignKey('migrations.id', ondelete='CASCADE'), nullable=False),
    Column('source_node_id', Integer, ForeignKey('kg_nodes.id', ondelete='CASCADE'), nullable=False),
    Column('relationship', String(80), nullable=False),
    Column('target_node_id', Integer, ForeignKey('kg_nodes.id', ondelete='CASCADE'), nullable=False),
    UniqueConstraint('migration_id', 'source_node_id', 'relationship', 'target_node_id'),
)
risk_catalog = Table('risk_catalog', metadata,
    Column('operation', String(80), primary_key=True),
    Column('risk_type', String(100), nullable=False),
    Column('severity', String(20), nullable=False),
    Column('explanation', Text, nullable=False),
    Column('impact', Text, nullable=False),
    Column('alternative', Text, nullable=False),
)


def initialize_database() -> None:
    metadata.create_all(engine)
    from .services.risk_catalog import RISK_CATALOG
    with engine.begin() as connection:
        for operation, rule in RISK_CATALOG.items():
            values = {'operation': operation, 'risk_type': rule['risk_type'], 'severity': rule['severity'], 'explanation': rule['explanation'], 'impact': rule['impact'], 'alternative': rule['alternative']}
            existing = connection.execute(select(risk_catalog.c.operation).where(risk_catalog.c.operation == operation)).first()
            if existing:
                connection.execute(risk_catalog.update().where(risk_catalog.c.operation == operation).values(**values))
            else:
                connection.execute(risk_catalog.insert().values(**values))


def database_info() -> dict[str, Any]:
    return {'url_scheme': DATABASE_URL.split(':', 1)[0], 'dialect': engine.dialect.name}
