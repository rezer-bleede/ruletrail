import { useEffect, useState } from 'react'
import api from '../api/client'
import { Rule, RulePackSummary } from '../types'

export function useRulepacks() {
  const [rulepacks, setRulepacks] = useState<RulePackSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    api
      .get<RulePackSummary[]>('/rulepacks/')
      .then((res) => setRulepacks(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return { rulepacks, loading, error }
}

export async function fetchRules(rulepackId: number) {
  const response = await api.get<Rule[]>(`/rulepacks/${rulepackId}/rules`)
  return response.data
}

export async function createRule(rulepackId: number, payload: Partial<Rule>) {
  const response = await api.post<Rule>(`/rulepacks/${rulepackId}/rules`, payload)
  return response.data
}

export async function updateRule(ruleId: number, payload: Partial<Rule>) {
  const response = await api.put<Rule>(`/rulepacks/rules/${ruleId}`, payload)
  return response.data
}

export async function deleteRule(ruleId: number) {
  await api.delete(`/rulepacks/rules/${ruleId}`)
}
