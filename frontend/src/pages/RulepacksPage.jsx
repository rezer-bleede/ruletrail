import { useMemo, useState } from 'react'
import {
  useRulepacks,
  useImportRulepack,
  useCreateRule,
  useUpdateRule,
  useDeleteRule,
  useBulkRuleUpdate,
  useExportRulepack,
} from '../hooks/useRuletrail'

export default function RulepacksPage() {
  const { data, isLoading } = useRulepacks()
  const importMutation = useImportRulepack()
  const createRuleMutation = useCreateRule()
  const updateRuleMutation = useUpdateRule()
  const deleteRuleMutation = useDeleteRule()
  const bulkRuleMutation = useBulkRuleUpdate()
  const exportRulepackMutation = useExportRulepack()
  const [tenantId, setTenantId] = useState('00000000-0000-0000-0000-000000000001')
  const [name, setName] = useState('ADAA Baseline')
  const [description, setDescription] = useState('Baseline rules imported from Excel')
  const [activeVersionId, setActiveVersionId] = useState('')
  const [selectedRules, setSelectedRules] = useState([])
  const [bulkSeverity, setBulkSeverity] = useState('Medium')
  const [bulkThreshold, setBulkThreshold] = useState('')

  const latestVersions = useMemo(() => {
    if (!data) return []
    return data.flatMap((pack) => pack.versions.map((version) => ({ ...version, rulepackName: pack.name })))
  }, [data])

  const activeVersion = latestVersions.find((version) => version.id === activeVersionId) || latestVersions[0]

  const [newRule, setNewRule] = useState({
    domain: '',
    group_name: '',
    rule_id: '',
    clause: '',
    severity: 'Medium',
    threshold: '',
    message: '',
    conditionField: '',
    conditionValue: '',
  })

  const resetNewRule = () =>
    setNewRule({
      domain: '',
      group_name: '',
      rule_id: '',
      clause: '',
      severity: 'Medium',
      threshold: '',
      message: '',
      conditionField: '',
      conditionValue: '',
    })

  return (
    <div className="space-y-6">
      <section className="presight-card">
        <h2 className="text-lg font-semibold text-presightBlue">Import Rulepack</h2>
        <p className="mt-1 text-sm text-slate-600">Upload Excel sheet(s) to create a versioned rulepack.</p>
        <form
          className="mt-4 grid gap-4 md:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault()
            const form = event.target
            const file = form.file.files[0]
            if (!file) return
            importMutation.mutate({
              file,
              metadata: { tenant_id: tenantId, name, description },
            })
          }}
        >
          <label className="flex flex-col gap-1 text-sm font-medium">
            Tenant ID
            <input
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              required
            />
          </label>
          <label className="flex flex-col gap-1 text-sm font-medium">
            Rulepack Name
            <input
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>
          <label className="flex flex-col gap-1 text-sm font-medium md:col-span-2">
            Description
            <textarea
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </label>
          <label className="flex flex-col gap-2 text-sm font-medium md:col-span-2">
            Excel File
            <input type="file" name="file" accept=".xlsx" className="rounded-md border border-slate-300 px-3 py-2 text-sm" required />
          </label>
          <button
            type="submit"
            className="md:col-span-2 rounded-full bg-presightTeal px-4 py-2 text-sm font-semibold text-white shadow hover:bg-presightTeal/80"
            disabled={importMutation.isPending}
          >
            {importMutation.isPending ? 'Importing…' : 'Import Rulepack'}
          </button>
        </form>
        {importMutation.isError && <p className="mt-3 text-sm text-red-500">{importMutation.error.message}</p>}
        {importMutation.isSuccess && <p className="mt-3 text-sm text-presightTeal">Rulepack imported successfully!</p>}
      </section>

      <section className="presight-card">
        <h2 className="text-lg font-semibold text-presightBlue">Versions</h2>
        {isLoading && <p className="mt-4 text-sm text-slate-500">Loading rulepacks…</p>}
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-2 text-left font-semibold text-slate-600">Rulepack</th>
                <th className="px-4 py-2 text-left font-semibold text-slate-600">Version</th>
                <th className="px-4 py-2 text-left font-semibold text-slate-600">Rules</th>
                <th className="px-4 py-2 text-left font-semibold text-slate-600">Published</th>
                <th className="px-4 py-2 text-left font-semibold text-slate-600">Checksum</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {latestVersions.map((version) => (
                <tr
                  key={version.id}
                  className={activeVersion?.id === version.id ? 'bg-presightTeal/10' : ''}
                  onClick={() => {
                    setActiveVersionId(version.id)
                    setSelectedRules([])
                  }}
                >
                  <td className="px-4 py-2 font-medium text-presightBlue">{version.rulepackName}</td>
                  <td className="px-4 py-2">{version.version}</td>
                  <td className="px-4 py-2">{version.rules.length}</td>
                  <td className="px-4 py-2">
                    <span className={`presight-chip ${version.published ? 'bg-presightTeal/20 text-presightBlue' : 'bg-slate-200 text-slate-600'}`}>
                      {version.published ? 'Published' : 'Draft'}
                    </span>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{version.checksum || '—'}</td>
                </tr>
              ))}
              {!latestVersions.length && !isLoading && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-slate-500">
                    No rulepacks found. Import one to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {activeVersion && (
        <section className="presight-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-presightBlue">Rule Management — {activeVersion.version}</h3>
              <p className="text-sm text-slate-500">Draft edits stay isolated until you publish the version.</p>
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() =>
                  bulkRuleMutation.mutate({
                    versionId: activeVersion.id,
                    payload: { rule_ids: selectedRules, action: 'enable' },
                  })
                }
                className="rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold text-white shadow disabled:opacity-40"
                disabled={!selectedRules.length}
              >
                Enable
              </button>
              <button
                type="button"
                onClick={() =>
                  bulkRuleMutation.mutate({
                    versionId: activeVersion.id,
                    payload: { rule_ids: selectedRules, action: 'disable' },
                  })
                }
                className="rounded-full bg-red-500 px-3 py-1 text-xs font-semibold text-white shadow disabled:opacity-40"
                disabled={!selectedRules.length}
              >
                Disable
              </button>
              <button
                type="button"
                onClick={() => exportRulepackMutation.mutate(activeVersion.id)}
                className="rounded-full bg-presightBlue px-3 py-1 text-xs font-semibold text-white shadow"
              >
                Export Excel/YAML
              </button>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {activeVersion.rules.map((rule) => (
              <div key={rule.id} className="rounded-lg border border-slate-200 p-4 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-base font-semibold text-presightBlue">{rule.rule_id}</h4>
                    <p className="text-xs uppercase tracking-wide text-slate-500">{rule.domain} · {rule.group_name}</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={selectedRules.includes(rule.id)}
                    onChange={(event) =>
                      setSelectedRules((prev) =>
                        event.target.checked ? [...prev, rule.id] : prev.filter((id) => id !== rule.id)
                      )
                    }
                  />
                </div>
                <p className="mt-2 text-sm text-slate-600">{rule.message}</p>
                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                  <span className="presight-chip bg-slate-200 text-slate-700">Severity: {rule.severity}</span>
                  <span className="presight-chip bg-slate-200 text-slate-700">Threshold: {rule.threshold || 'n/a'}</span>
                  <span className={`presight-chip ${rule.enabled ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                    {rule.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                  {Object.entries(rule.condition).map(([field, detail]) => (
                    <span key={field} className="rounded-full bg-slate-100 px-3 py-1 font-mono">
                      {field} {detail.operator} {detail.value}
                    </span>
                  ))}
                </div>
                <div className="mt-4 flex flex-wrap gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() =>
                      updateRuleMutation.mutate({
                        ruleId: rule.id,
                        payload: { enabled: !rule.enabled },
                      })
                    }
                    className="rounded-full bg-presightTeal px-3 py-1 font-semibold text-white"
                  >
                    Toggle
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      deleteRuleMutation.mutate(rule.id)
                    }
                    className="rounded-full bg-red-500 px-3 py-1 font-semibold text-white"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
            {!activeVersion.rules.length && <p className="text-sm text-slate-500">No rules yet.</p>}
          </div>

          {selectedRules.length > 0 && (
            <div className="rounded-lg border border-slate-200 p-4 text-sm">
              <h4 className="font-semibold text-presightBlue">Bulk Adjustments</h4>
              <div className="mt-3 flex flex-wrap gap-4">
                <label className="flex items-center gap-2">
                  Severity
                  <select
                    value={bulkSeverity}
                    onChange={(e) => setBulkSeverity(e.target.value)}
                    className="rounded-md border border-slate-300 px-2 py-1"
                  >
                    <option>Critical</option>
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                  <button
                    type="button"
                    onClick={() =>
                      bulkRuleMutation.mutate({
                        versionId: activeVersion.id,
                        payload: { rule_ids: selectedRules, action: 'set_severity', value: bulkSeverity },
                      })
                    }
                    className="rounded-full bg-presightTeal px-3 py-1 text-xs font-semibold text-white"
                  >
                    Apply
                  </button>
                </label>
                <label className="flex items-center gap-2">
                  Threshold
                  <input
                    value={bulkThreshold}
                    onChange={(e) => setBulkThreshold(e.target.value)}
                    className="rounded-md border border-slate-300 px-2 py-1"
                  />
                  <button
                    type="button"
                    onClick={() =>
                      bulkRuleMutation.mutate({
                        versionId: activeVersion.id,
                        payload: { rule_ids: selectedRules, action: 'set_threshold', value: bulkThreshold },
                      })
                    }
                    className="rounded-full bg-presightTeal px-3 py-1 text-xs font-semibold text-white"
                  >
                    Apply
                  </button>
                </label>
              </div>
            </div>
          )}

          <div className="rounded-lg border border-dashed border-presightTeal/50 p-4">
            <h4 className="font-semibold text-presightBlue">Add Rule</h4>
            <form
              className="mt-3 grid gap-3 md:grid-cols-3"
              onSubmit={(event) => {
                event.preventDefault()
                createRuleMutation.mutate({
                  versionId: activeVersion.id,
                  payload: {
                    domain: newRule.domain,
                    group_name: newRule.group_name,
                    rule_id: newRule.rule_id,
                    clause: newRule.clause,
                    severity: newRule.severity,
                    threshold: newRule.threshold,
                    message: newRule.message,
                    mappings: {},
                    condition: {
                      [newRule.conditionField]: { operator: '==', value: newRule.conditionValue },
                    },
                  },
                })
                resetNewRule()
              }}
            >
              {[
                ['domain', 'Domain'],
                ['group_name', 'Group'],
                ['rule_id', 'Rule ID'],
                ['clause', 'Clause'],
                ['severity', 'Severity'],
                ['threshold', 'Threshold'],
                ['message', 'Message'],
                ['conditionField', 'Condition Field'],
                ['conditionValue', 'Condition Value'],
              ].map(([key, label]) => (
                <label key={key} className="flex flex-col gap-1 text-xs font-medium">
                  {label}
                  <input
                    required={['domain', 'group_name', 'rule_id', 'message', 'conditionField', 'conditionValue'].includes(key)}
                    value={newRule[key]}
                    onChange={(e) => setNewRule((prev) => ({ ...prev, [key]: e.target.value }))}
                    className="rounded-md border border-slate-300 px-2 py-1"
                  />
                </label>
              ))}
              <button
                type="submit"
                className="md:col-span-3 rounded-full bg-presightTeal px-4 py-2 text-xs font-semibold text-white"
              >
                Create Rule
              </button>
            </form>
          </div>

          {exportRulepackMutation.isSuccess && (
            <div className="rounded-md border border-presightTeal/40 bg-presightTeal/10 px-4 py-3 text-xs text-presightBlue">
              Exported to {exportRulepackMutation.data.excel} and {exportRulepackMutation.data.yaml}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
