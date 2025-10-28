import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchRunDetail } from '../hooks/useRuns'
import { DecisionTrace, RunDetail, RunRuleResult } from '../types'

interface BreadcrumbItem {
  label: string
  onClick?: () => void
}

export default function ResultsPage() {
  const { runId } = useParams()
  const [run, setRun] = useState<RunDetail | null>(null)
  const [selectedRule, setSelectedRule] = useState<RunRuleResult | null>(null)
  const [selectedTrace, setSelectedTrace] = useState<DecisionTrace | null>(null)
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([])

  useEffect(() => {
    if (runId) {
      fetchRunDetail(Number(runId)).then((detail) => {
        setRun(detail)
        if (detail.rule_results.length) {
          setSelectedRule(detail.rule_results[0])
        }
      })
    }
  }, [runId])

  useEffect(() => {
    const crumbs: BreadcrumbItem[] = [{ label: 'Run Summary', onClick: () => setSelectedTrace(null) }]
    if (selectedRule) {
      crumbs.push({ label: selectedRule.summary.new_rule_name, onClick: () => setSelectedTrace(null) })
    }
    if (selectedTrace) {
      crumbs.push({ label: `Record ${selectedTrace.record_id}` })
    }
    setBreadcrumbs(crumbs)
  }, [selectedRule, selectedTrace])

  if (!run) {
    return <p className="text-sm text-slate-500">Loading run…</p>
  }

  const statusBadges = Object.entries(run.status_counts || {})

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-presight-primary">Run #{run.id}</h1>
          <p className="text-sm text-slate-500">Domain: {run.domain}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {statusBadges.map(([label, count]) => (
            <span key={label} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
              {label}: {count}
            </span>
          ))}
        </div>
      </div>

      <nav className="flex items-center gap-2 text-xs text-slate-500">
        {breadcrumbs.map((crumb, index) => (
          <span key={`${crumb.label}-${index}`} className="flex items-center gap-2">
            {index > 0 && <span>›</span>}
            {crumb.onClick ? (
              <button className="text-presight-primary" onClick={crumb.onClick}>
                {crumb.label}
              </button>
            ) : (
              <span>{crumb.label}</span>
            )}
          </span>
        ))}
      </nav>

      <div className="grid gap-6 lg:grid-cols-[320px,1fr]">
        <aside className="rounded-xl border border-slate-200 p-4">
          <h2 className="text-sm font-semibold text-slate-600">Rules</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {run.rule_results.map((rule) => (
              <li key={rule.id}>
                <button
                  onClick={() => {
                    setSelectedRule(rule)
                    setSelectedTrace(null)
                  }}
                  className={`w-full rounded-lg border px-3 py-2 text-left ${
                    selectedRule?.id === rule.id
                      ? 'border-presight-primary bg-presight-surface text-presight-primary'
                      : 'border-transparent hover:border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">{rule.summary.new_rule_name}</span>
                    <span className="text-xs uppercase text-slate-400">{rule.status}</span>
                  </div>
                  <div className="text-xs text-slate-500">Rule #{rule.summary.rule_no}</div>
                </button>
              </li>
            ))}
          </ul>
        </aside>
        <section className="space-y-4">
          {selectedTrace ? (
            <TraceDetail trace={selectedTrace} onBack={() => setSelectedTrace(null)} />
          ) : selectedRule ? (
            <RuleDetail rule={selectedRule} onSelectTrace={setSelectedTrace} />
          ) : (
            <p className="text-sm text-slate-500">Select a rule to inspect decisions.</p>
          )}
        </section>
      </div>
    </div>
  )
}

function RuleDetail({ rule, onSelectTrace }: { rule: RunRuleResult; onSelectTrace: (trace: DecisionTrace) => void }) {
  return (
    <div className="rounded-xl border border-slate-200">
      <header className="border-b border-slate-200 bg-slate-50 px-5 py-4">
        <h2 className="text-lg font-semibold text-slate-700">{rule.summary.new_rule_name}</h2>
        <p className="text-xs text-slate-500">Status: {rule.status}</p>
      </header>
      <div className="divide-y divide-slate-200">
        {rule.decisions.map((decision) => (
          <button
            key={decision.id}
            onClick={() => onSelectTrace(decision)}
            className="w-full px-5 py-4 text-left hover:bg-slate-50"
          >
            <div className="flex items-center justify-between text-sm">
              <span className="font-semibold text-slate-700">Record {decision.record_id}</span>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                {decision.status}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">{decision.rationale}</p>
          </button>
        ))}
        {!rule.decisions.length && (
          <p className="px-5 py-6 text-sm text-slate-400">No records evaluated.</p>
        )}
      </div>
    </div>
  )
}

function TraceDetail({ trace, onBack }: { trace: DecisionTrace; onBack: () => void }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-presight-primary">Record {trace.record_id}</h2>
          <p className="text-xs uppercase text-slate-500">Decision: {trace.status}</p>
        </div>
        <button onClick={onBack} className="rounded-lg border border-slate-200 px-3 py-1 text-xs text-slate-600">
          Back to rule
        </button>
      </div>
      <div className="rounded-xl border border-slate-200">
        <div className="border-b border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-600">Inputs</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <tbody>
            {Object.entries(trace.inputs || {}).map(([field, value]) => (
              <tr key={field} className="divide-x divide-slate-200">
                <td className="px-4 py-2 font-medium text-slate-600">{field}</td>
                <td className="px-4 py-2 text-slate-500">{String(value)}</td>
              </tr>
            ))}
            {!Object.keys(trace.inputs || {}).length && (
              <tr>
                <td className="px-4 py-4 text-sm text-slate-400">No inputs captured.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="rounded-xl border border-slate-200">
        <div className="border-b border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-600">Clause Evaluation</div>
        <ul className="divide-y divide-slate-200 text-sm">
          {trace.clauses.map((clause, index) => (
            <li key={index} className="px-4 py-3">
              <div className="flex items-center justify-between">
                <span className="font-medium text-slate-600">
                  {clause.field} {clause.operator} {String(clause.value)}
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    clause.result ? 'bg-presight-success/20 text-presight-success' : 'bg-presight-danger/20 text-presight-danger'
                  }`}
                >
                  {clause.result ? 'True' : 'False'}
                </span>
              </div>
              {clause.connector && <p className="text-xs text-slate-400">Connector: {clause.connector}</p>}
            </li>
          ))}
          {!trace.clauses.length && <li className="px-4 py-6 text-sm text-slate-400">No clauses stored.</li>}
        </ul>
      </div>
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        <p className="font-semibold text-presight-primary">Rationale</p>
        <p className="mt-2 text-slate-600">{trace.rationale}</p>
      </div>
    </div>
  )
}
