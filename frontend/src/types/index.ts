export type StatusLabel = 'PASS' | 'FAIL' | 'WARN' | 'N/A'

export interface ConditionClause {
  field: string
  operator: string
  value: any
  connector?: string | null
}

export interface Rule {
  id: number
  rule_no: string
  new_rule_name: string
  order_index: number
  sub_vertical?: string
  conditions: ConditionClause[]
  rule_logic_business?: string
  de_rule_logic?: string
  original_fields: string[]
  aggregated_fields: string[]
  adaa_status?: string
  uaeaa_status?: string
}

export interface RulePackSummary {
  id: number
  domain: string
  version: number
  checksum: string
  uploaded_at: string
}

export interface RulePack extends RulePackSummary {
  rules: Rule[]
}

export interface Dataset {
  id: number
  name: string
  host: string
  index_name: string
  query: Record<string, unknown>
}

export interface RunSummary {
  id: number
  domain: string
  status_counts: Record<string, number>
  started_at: string
  completed_at?: string
}

export interface DecisionTrace {
  id: number
  record_id: string
  status: StatusLabel | string
  rationale?: string
  inputs: Record<string, any>
  clauses: Array<Record<string, any>>
}

export interface RunRuleResult {
  id: number
  rule_id: number
  status: StatusLabel | string
  summary: Record<string, any>
  decisions: DecisionTrace[]
}

export interface RunDetail {
  id: number
  domain: string
  rulepack_id: number
  status_counts: Record<string, number>
  rule_results: RunRuleResult[]
}
