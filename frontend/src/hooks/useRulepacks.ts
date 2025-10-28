import { useCallback, useEffect, useState } from 'react'
import api from '../api/client'
import { Rule, RulePackSummary } from '../types'

export function useRulepacks() {
  const [rulepacks, setRulepacks] = useState<RulePackSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async (): Promise<RulePackSummary[]> => {
    setLoading(true)
    try {
      const res = await api.get<RulePackSummary[]>('/rulepacks/')
      setRulepacks(res.data)
      setError(null)
      return res.data
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh().catch(() => null)
  }, [refresh])

  return { rulepacks, loading, error, refresh }
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

export async function importRulepacks(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post<RulePackSummary[]>('/rulepacks/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}
