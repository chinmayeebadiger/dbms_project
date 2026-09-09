# Database Schema and Knowledge Graph

## Relational database schema

```mermaid
erDiagram
    MIGRATIONS ||--o{ DETECTED_RISKS : contains
    MIGRATIONS ||--o{ KG_NODES : scopes
    MIGRATIONS ||--o{ KG_EDGES : scopes
    KG_NODES ||--o{ KG_EDGES : source
    KG_NODES ||--o{ KG_EDGES : target

    MIGRATIONS {
        uuid id PK
        varchar title
        text sql_text
        numeric risk_score
        varchar risk_level
        jsonb statements
        jsonb warnings
        timestamptz created_at
    }

    DETECTED_RISKS {
        bigint id PK
        uuid migration_id FK
        varchar operation
        varchar affected_object
        varchar risk_type
        varchar severity
        text explanation
        text impact
        text alternative
        integer line_number
    }

    KG_NODES {
        bigint id PK
        uuid migration_id FK
        varchar node_type
        varchar node_key
        varchar label
    }

    KG_EDGES {
        bigint id PK
        uuid migration_id FK
        bigint source_node_id FK
        varchar relationship
        bigint target_node_id FK
    }

    RISK_CATALOG {
        varchar operation PK
        varchar risk_type
        varchar severity
        text explanation
        text impact
        text alternative
    }
```

## Knowledge graph model

```mermaid
flowchart LR
    OP[Operation<br/>DROP_COLUMN]
    OBJ[Database Object<br/>customers.email]
    RISK[Risk<br/>DATA_LOSS]
    SEV[Severity<br/>CRITICAL]
    COND[Condition<br/>WITHOUT_WHERE_CLAUSE]
    ALT[Safer Alternative<br/>DEPRECATE_BEFORE_DROP]

    OP -->|AFFECTS| OBJ
    OP -->|MAY_CAUSE| RISK
    OP -->|HAS_CONDITION| COND
    COND -->|INCREASES| RISK
    RISK -->|HAS_SEVERITY| SEV
    RISK -->|HAS_ALTERNATIVE| ALT
```

## Stored graph relationship flow

```mermaid
flowchart TD
    M[MIGRATIONS] --> F[DETECTED_RISKS]
    F --> O[Operation node]
    F --> D[Database Object node]
    F --> R[Risk node]
    F --> S[Severity node]
    F --> A[Safer Alternative node]
    O -. AFFECTS .-> D
    O -. MAY_CAUSE .-> R
    R -. HAS_SEVERITY .-> S
    R -. HAS_ALTERNATIVE .-> A
```

The `migration_id` on graph nodes and edges keeps each visualization scoped to one analyzed migration. The `risk_catalog` table is the reusable reference catalog; `detected_risks` stores the findings generated for an individual migration.
