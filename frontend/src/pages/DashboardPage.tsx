import { useMemo } from 'react'
import { useRuns } from '../hooks/useRuns'

const domains = ['HR', 'Finance', 'Revenue', 'IT', 'Proc', 'Forensic', 'COI']

export default function DashboardPage() {
  const { runs, loading } = useRuns()

  const summaries = useMemo(() => {
    const latestByDomain = new Map<string, typeof runs[number]>()
    runs.forEach((run) => {
      if (!latestByDomain.has(run.domain)) {
        latestByDomain.set(run.domain, run)
      }
    })
    return domains.map((domain) => ({ domain, run: latestByDomain.get(domain) }))
  }, [runs])

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-presight-primary">Dashboard</h1>
        <p className="text-xs text-slate-500">Latest evaluation health by domain</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {summaries.map(({ domain, run }) => (
          <div key={domain} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-700">{domain}</h2>
              <span className="text-[11px] uppercase tracking-wide text-slate-400">{run ? 'Latest run' : 'No runs yet'}</span>
            </div>
            {loading && <p className="mt-2 text-sm text-slate-400">Loading…</p>}
            {run ? (
              <div className="mt-3 space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-presight-primary">Status</span>
                  <span>{Object.entries(run.status_counts).map(([label, value]) => `${label}: ${value}`).join(' • ')}</span>
                </div>
                <div className="text-xs text-slate-500">
                  Started {new Date(run.started_at).toLocaleString()}
                </div>
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-500">Start an evaluation to populate this tile.</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
