import { useState } from 'react'
import { useRunDetails, useExportRun } from '../hooks/useRuletrail'

function DecisionBadge({ decision }) {
  const colors = {
    PASS: 'bg-emerald-100 text-emerald-800',
    FAIL: 'bg-red-100 text-red-700',
    WARN: 'bg-amber-100 text-amber-700',
    NA: 'bg-slate-200 text-slate-600',
  }
  return <span className={`presight-chip ${colors[decision] || colors.NA}`}>{decision}</span>
}

export default function ResultsExplorerPage() {
  const [runId, setRunId] = useState('')
  const [selectedRun, setSelectedRun] = useState(null)
  const { data: runDetails, refetch, isFetching } = useRunDetails(selectedRun)
  const exportMutation = useExportRun()

  return (
    <div className="space-y-6">
      <section className="presight-card">
        <h2 className="text-lg font-semibold text-presightBlue">Retrieve Run</h2>
        <form
          className="mt-4 flex flex-wrap items-end gap-4"
          onSubmit={(event) => {
            event.preventDefault()
            setSelectedRun(runId)
            refetch()
          }}
        >
          <label className="flex flex-col text-sm font-medium">
            Run ID
            <input
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              value={runId}
              onChange={(event) => setRunId(event.target.value)}
              placeholder="Paste a run identifier"
              required
            />
          </label>
          <button
            type="submit"
            className="rounded-full bg-presightTeal px-4 py-2 text-sm font-semibold text-white shadow hover:bg-presightTeal/80"
          >
            View Results
          </button>
          {runDetails && (
            <button
              type="button"
              onClick={() => exportMutation.mutate(runDetails.id)}
              className="rounded-full bg-presightBlue px-4 py-2 text-sm font-semibold text-white shadow hover:bg-presightBlue/80"
            >
              Export Artifacts
            </button>
          )}
        </form>
        {isFetching && <p className="mt-3 text-sm text-slate-500">Loading run results…</p>}
        {exportMutation.isSuccess && (
          <p className="mt-3 text-sm text-presightTeal">
            Artifacts generated. JSON hash: <span className="font-mono">{exportMutation.data.artifacts.json.sha256}</span>
          </p>
        )}
      </section>

      {runDetails && (
        <section className="space-y-4">
          <div className="presight-card">
            <h3 className="text-lg font-semibold text-presightBlue">Overview</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-4">
              <div>
                <p className="text-xs font-semibold uppercase text-slate-500">Run ID</p>
                <p className="font-mono text-sm">{runDetails.id}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-slate-500">Rulepack Version</p>
                <p className="text-sm">{runDetails.rulepack_version_id}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-slate-500">Status</p>
                <p className="text-sm capitalize">{runDetails.status}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-slate-500">Records Evaluated</p>
                <p className="text-sm">{runDetails.results.reduce((acc, result) => acc + result.affected_records, 0)}</p>
              </div>
            </div>
          </div>

          {runDetails.results.map((result) => (
            <div key={result.id} className="presight-card space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-semibold text-presightBlue">Rule {result.rule_id}</h4>
                  <p className="text-sm text-slate-500">{result.narrative}</p>
                </div>
                <DecisionBadge decision={result.decision} />
              </div>
              <div className="rounded-lg border border-slate-200">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-3 py-2 text-left font-semibold text-slate-600">Entity</th>
                      <th className="px-3 py-2 text-left font-semibold text-slate-600">Decision</th>
                      <th className="px-3 py-2 text-left font-semibold text-slate-600">Inputs</th>
                      <th className="px-3 py-2 text-left font-semibold text-slate-600">Thresholds</th>
                      <th className="px-3 py-2 text-left font-semibold text-slate-600">Trace</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {result.records.map((record) => (
                      <tr key={record.id}>
                        <td className="px-3 py-2 font-mono text-xs">{record.entity_id}</td>
                        <td className="px-3 py-2"><DecisionBadge decision={record.decision} /></td>
                        <td className="px-3 py-2">
                          <ul className="space-y-1 text-xs">
                            {Object.entries(record.inputs).map(([key, value]) => (
                              <li key={key}>
                                <span className="font-semibold">{key}</span>: {value}
                              </li>
                            ))}
                          </ul>
                        </td>
                        <td className="px-3 py-2 text-xs">
                          {Object.entries(record.thresholds).map(([key, value]) => (
                            <div key={key}>
                              <span className="font-semibold">{key}</span>: {value}
                            </div>
                          ))}
                        </td>
                        <td className="px-3 py-2 text-xs">
                          {Object.entries(record.trace).map(([field, detail]) => (
                            <div key={field}>
                              <p className="font-semibold">{field}</p>
                              <p>{detail.detail}</p>
                            </div>
                          ))}
                        </td>
                      </tr>
                    ))}
                    {!result.records.length && (
                      <tr>
                        <td colSpan={5} className="px-3 py-6 text-center text-sm text-slate-500">
                          No records violated this rule.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  )
}
