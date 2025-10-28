import { useEffect, useState } from 'react'
import api from '../api/client'
import { RunDetail, RunRuleResult, RunSummary } from '../types'

export function useRuns() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = () => {
    setLoading(true)
    api
      .get<RunSummary[]>('/runs/')
      .then((res) => setRuns(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { runs, loading, error, refresh }
}

export async function fetchRunDetail(runId: number) {
  const [runRes, ruleRes] = await Promise.all([
    api.get<RunDetail>(`/runs/${runId}`),
    api.get<RunRuleResult[]>(`/runs/${runId}/rules`)
  ])
  return { ...runRes.data, rule_results: ruleRes.data }
}
