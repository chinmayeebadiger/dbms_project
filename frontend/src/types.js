export const riskLevels = ['Low', 'Medium', 'High', 'Critical']

export const emptyAnalysis = {
  migration_id: null,
  title: '',
  overall_score: 0,
  risk_level: 'Low',
  statements: [],
  findings: [],
}

export const mockAnalysis = {
  migration_id: 'demo-001',
  title: 'Customer table cleanup',
  overall_score: 90,
  risk_level: 'Critical',
  statements: [
    { line_number: 1, operation: 'DROP_COLUMN', raw_sql: 'ALTER TABLE customers DROP COLUMN email;' },
    { line_number: 2, operation: 'UPDATE_WITHOUT_WHERE', raw_sql: 'UPDATE customers SET active = false;' },
  ],
  findings: [
    {
      operation: 'DROP_COLUMN',
      affected_object: 'customers.email',
      risk_type: 'DATA_LOSS',
      severity: 'CRITICAL',
      explanation: 'Dropping the column permanently removes stored values.',
      impact: 'Existing data and application queries may be affected.',
      alternative: 'Deprecate the column, back it up, and remove it later.',
      line_number: 1,
    },
    {
      operation: 'UPDATE_WITHOUT_WHERE',
      affected_object: 'customers',
      risk_type: 'MASS_UPDATE',
      severity: 'HIGH',
      explanation: 'An UPDATE without a WHERE clause changes every row.',
      impact: 'All customer records could be modified unintentionally.',
      alternative: 'Add a condition, preview affected rows, and define a rollback plan.',
      line_number: 2,
    },
  ],
}

export const mockHistory = [
  { id: 'demo-001', title: 'Customer table cleanup', risk_level: 'Critical', risk_score: 90, created_at: 'Today, 10:24 AM', findings_count: 2 },
  { id: 'demo-002', title: 'Add customer phone number', risk_level: 'Low', risk_score: 12, created_at: 'Yesterday, 3:10 PM', findings_count: 0 },
  { id: 'demo-003', title: 'Orders index refresh', risk_level: 'Medium', risk_score: 42, created_at: 'Sep 06, 2026', findings_count: 1 },
]

export const mockGraph = {
  nodes: [
    { id: 'op-1', node_type: 'Operation', label: 'DROP_COLUMN' },
    { id: 'obj-1', node_type: 'Database Object', label: 'customers.email' },
    { id: 'risk-1', node_type: 'Risk', label: 'DATA_LOSS' },
    { id: 'sev-1', node_type: 'Severity', label: 'CRITICAL' },
    { id: 'alt-1', node_type: 'Safer Alternative', label: 'DEPRECATE_BEFORE_DROP' },
  ],
  edges: [
    { id: 'edge-1', source: 'op-1', target: 'obj-1', relationship: 'AFFECTS' },
    { id: 'edge-2', source: 'op-1', target: 'risk-1', relationship: 'MAY_CAUSE' },
    { id: 'edge-3', source: 'risk-1', target: 'sev-1', relationship: 'HAS_SEVERITY' },
    { id: 'edge-4', source: 'risk-1', target: 'alt-1', relationship: 'HAS_ALTERNATIVE' },
  ],
}
