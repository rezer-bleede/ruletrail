import { Link } from 'react-router-dom'
import { useRuns } from '../hooks/useRuns'

export default function RunsPage() {
  const { runs, loading } = useRuns()

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-presight-primary">Runs</h1>
        <p className="text-xs text-slate-500">Review historical evaluations</p>
      </div>
      <div className="overflow-hidden rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-100 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2.5">Run ID</th>
              <th className="px-3 py-2.5">Domain</th>
              <th className="px-3 py-2.5">Summary</th>
              <th className="px-3 py-2.5">Started</th>
              <th className="px-3 py-2.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {runs.map((run) => (
              <tr key={run.id} className="hover:bg-slate-50">
                <td className="px-3 py-2.5 font-medium text-slate-700">#{run.id}</td>
                <td className="px-3 py-2.5">{run.domain}</td>
                <td className="px-3 py-2.5 text-slate-500">
                  {Object.entries(run.status_counts)
                    .map(([status, count]) => `${status}: ${count}`)
                    .join(' • ')}
                </td>
                <td className="px-3 py-2.5 text-xs text-slate-500">{new Date(run.started_at).toLocaleString()}</td>
                <td className="px-3 py-2.5 text-sm">
                  <Link to={`/results/${run.id}`} className="text-presight-primary hover:underline">
                    View results
                  </Link>
                </td>
              </tr>
            ))}
            {!runs.length && (
              <tr>
                <td colSpan={5} className="px-3 py-10 text-center text-sm text-slate-400">
                  {loading ? 'Loading runs…' : 'No runs available yet.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
