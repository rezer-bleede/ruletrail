import { useEffect, useState } from 'react'
import { useRulepacks, useAuditLogs } from '../hooks/useRuletrail'

const kpiCards = [
  { label: 'Active Rulepacks', value: (data) => data?.length || 0 },
  { label: 'Published Versions', value: (data) => data?.reduce((acc, rp) => acc + rp.versions.filter((v) => v.published).length, 0) || 0 },
  { label: 'Total Rules', value: (data) => data?.reduce((acc, rp) => acc + rp.versions[0]?.rules?.length || 0, 0) || 0 },
]

export default function DashboardPage() {
  const { data: rulepacks } = useRulepacks()
  const { data: auditLogs } = useAuditLogs()
  const [recent, setRecent] = useState([])

  useEffect(() => {
    if (auditLogs) {
      setRecent(auditLogs.slice(0, 5))
    }
  }, [auditLogs])

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-3">
        {kpiCards.map((card) => (
          <div key={card.label} className="presight-card">
            <p className="text-sm uppercase tracking-wide text-slate-500">{card.label}</p>
            <p className="mt-2 text-3xl font-semibold text-presightBlue">{card.value(rulepacks)}</p>
          </div>
        ))}
      </section>

      <section className="presight-card">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-presightBlue">Recent Activity</h2>
        </div>
        <div className="mt-4 space-y-3">
          {recent.map((log) => (
            <div key={log.id} className="flex items-center justify-between border-b border-slate-200 pb-2 last:border-0">
              <div>
                <p className="font-medium">{log.action}</p>
                <p className="text-xs text-slate-500">{log.details?.version || ''}</p>
              </div>
              <span className="text-xs text-slate-400">{new Date(log.created_at).toLocaleString()}</span>
            </div>
          ))}
          {!recent.length && <p className="text-sm text-slate-500">No activity yet.</p>}
        </div>
      </section>
    </div>
  )
}
