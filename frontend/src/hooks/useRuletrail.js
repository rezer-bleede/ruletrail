import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'

export function useRulepacks() {
  return useQuery({
    queryKey: ['rulepacks'],
    queryFn: api.getRulepacks,
  })
}

export function useImportRulepack() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ file, metadata }) => {
      const formData = new FormData()
      formData.append('file', file)
      return api.importRulepack(formData, metadata)
    },
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ['rulepacks'] })
    },
  })
}

export function useCreateRule() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ versionId, payload }) => api.createRule(versionId, payload),
    onSuccess: () => client.invalidateQueries({ queryKey: ['rulepacks'] }),
  })
}

export function useUpdateRule() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ ruleId, payload }) => api.updateRule(ruleId, payload),
    onSuccess: () => client.invalidateQueries({ queryKey: ['rulepacks'] }),
  })
}

export function useDeleteRule() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (ruleId) => api.deleteRule(ruleId),
    onSuccess: () => client.invalidateQueries({ queryKey: ['rulepacks'] }),
  })
}

export function useBulkRuleUpdate() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ versionId, payload }) => api.bulkUpdateRules(versionId, payload),
    onSuccess: () => client.invalidateQueries({ queryKey: ['rulepacks'] }),
  })
}

export function useRun(rulepackVersionId) {
  return useMutation({
    mutationFn: (payload) => api.startRun(payload),
  })
}

export function useRunDetails(runId) {
  return useQuery({
    queryKey: ['run', runId],
    queryFn: () => api.listRuns(runId),
    enabled: !!runId,
    refetchInterval: runId ? 5000 : false,
  })
}

export function useExportRun() {
  return useMutation({
    mutationFn: (runId) => api.exportRun(runId),
  })
}

export function useExportRulepack() {
  return useMutation({
    mutationFn: (versionId) => api.exportRulepack(versionId),
  })
}

export function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: api.settings,
  })
}

export function useAuditLogs() {
  return useQuery({
    queryKey: ['audit'],
    queryFn: api.auditLogs,
  })
}
