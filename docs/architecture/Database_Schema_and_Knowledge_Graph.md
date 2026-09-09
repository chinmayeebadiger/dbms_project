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

## Complete seeded knowledge graph

```mermaid
flowchart LR
    subgraph OPS[Migration operations]
        DT[DROP_TABLE]
        DC[DROP_COLUMN]
        TT[TRUNCATE_TABLE]
        DW[DELETE_WITHOUT_WHERE]
        UW[UPDATE_WITHOUT_WHERE]
        AT[ALTER_COLUMN_TYPE]
        RC[RENAME_COLUMN]
        NN[ADD_NOT_NULL]
        AU[ADD_UNIQUE]
        AF[ADD_FOREIGN_KEY]
        CI[CREATE_INDEX]
        DI[DROP_INDEX]
    end

    subgraph OBJECTS[Database objects]
        TBL[TABLE]
        COL[COLUMN]
        CON[CONSTRAINT]
        IDX[INDEX]
    end

    subgraph RISKS[Risk types]
        DL[DATA_LOSS]
        FTD[FULL_TABLE_DELETION]
        MU[MASS_UPDATE]
        TC[TYPE_CHANGE]
        CB[COMPATIBILITY_BREAK]
        DF[DEPLOYMENT_FAILURE]
        CF[CONSTRAINT_FAILURE]
        RF[REFERENTIAL_FAILURE]
        LOCK[DEPLOYMENT_LOCK]
        PD[PERFORMANCE_DEGRADATION]
    end

    subgraph SEVERITY[Severity levels]
        CR[CRITICAL]
        HI[HIGH]
        MH[MEDIUM_HIGH]
        ME[MEDIUM]
    end

    subgraph ALT[Safer alternatives]
        BBD[BACKUP_BEFORE_DROP]
        DBD[DEPRECATE_BEFORE_DROP]
        BA[BACKUP_AND_APPROVE]
        WAP[ADD_WHERE_AND_PREVIEW]
        WAR[ADD_WHERE_AND_ROLLBACK]
        BIB[BACKFILL_IN_BATCHES]
        GCM[GRADUAL_COLUMN_MIGRATION]
        BTC[BACKFILL_THEN_CONSTRAIN]
        CDF[CHECK_DUPLICATES_FIRST]
        COF[CHECK_ORPHANS_FIRST]
        CC[CREATE_CONCURRENTLY]
        CIU[CHECK_INDEX_USAGE]
    end

    DT -->|AFFECTS| TBL
    DT -->|MAY_CAUSE| DL
    DT -->|HAS_SEVERITY| CR
    DT -->|HAS_ALTERNATIVE| BBD

    DC -->|AFFECTS| COL
    DC -->|MAY_CAUSE| DL
    DC -->|HAS_SEVERITY| CR
    DC -->|HAS_ALTERNATIVE| DBD

    TT -->|AFFECTS| TBL
    TT -->|MAY_CAUSE| DL
    TT -->|HAS_SEVERITY| CR
    TT -->|HAS_ALTERNATIVE| BA

    DW -->|AFFECTS| TBL
    DW -->|MAY_CAUSE| FTD
    DW -->|HAS_SEVERITY| CR
    DW -->|HAS_ALTERNATIVE| WAP

    UW -->|AFFECTS| TBL
    UW -->|MAY_CAUSE| MU
    UW -->|HAS_SEVERITY| HI
    UW -->|HAS_ALTERNATIVE| WAR

    AT -->|AFFECTS| COL
    AT -->|MAY_CAUSE| TC
    AT -->|HAS_SEVERITY| HI
    AT -->|HAS_ALTERNATIVE| BIB

    RC -->|AFFECTS| COL
    RC -->|MAY_CAUSE| CB
    RC -->|HAS_SEVERITY| HI
    RC -->|HAS_ALTERNATIVE| GCM

    NN -->|AFFECTS| COL
    NN -->|MAY_CAUSE| DF
    NN -->|HAS_SEVERITY| HI
    NN -->|HAS_ALTERNATIVE| BTC

    AU -->|AFFECTS| CON
    AU -->|MAY_CAUSE| CF
    AU -->|HAS_SEVERITY| MH
    AU -->|HAS_ALTERNATIVE| CDF

    AF -->|AFFECTS| CON
    AF -->|MAY_CAUSE| RF
    AF -->|HAS_SEVERITY| MH
    AF -->|HAS_ALTERNATIVE| COF

    CI -->|AFFECTS| IDX
    CI -->|MAY_CAUSE| LOCK
    CI -->|HAS_SEVERITY| ME
    CI -->|HAS_ALTERNATIVE| CC

    DI -->|AFFECTS| IDX
    DI -->|MAY_CAUSE| PD
    DI -->|HAS_SEVERITY| ME
    DI -->|HAS_ALTERNATIVE| CIU
```
