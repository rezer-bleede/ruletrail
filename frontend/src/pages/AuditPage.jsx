import { useAuditLogs } from '../hooks/useRuletrail'

export default function AuditPage() {
  const { data, isLoading } = useAuditLogs()

  return (
    <div className="presight-card">
      <h2 className="text-lg font-semibold text-presightBlue">Audit Trail</h2>
      {isLoading && <p className="mt-3 text-sm text-slate-500">Loading audit logs…</p>}
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-3 py-2 text-left font-semibold text-slate-600">Time</th>
              <th className="px-3 py-2 text-left font-semibold text-slate-600">Actor</th>
              <th className="px-3 py-2 text-left font-semibold text-slate-600">Action</th>
              <th className="px-3 py-2 text-left font-semibold text-slate-600">Target</th>
              <th className="px-3 py-2 text-left font-semibold text-slate-600">Metadata</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data?.map((log) => (
              <tr key={log.id}>
                <td className="px-3 py-2 text-xs text-slate-500">{new Date(log.created_at).toLocaleString()}</td>
                <td className="px-3 py-2">{log.actor}</td>
                <td className="px-3 py-2 font-medium text-presightBlue">{log.action}</td>
                <td className="px-3 py-2">{log.target_type} {log.target_id}</td>
                <td className="px-3 py-2 text-xs">{JSON.stringify(log.details)}</td>
              </tr>
            ))}
            {!data?.length && !isLoading && (
              <tr>
                <td colSpan={5} className="px-3 py-6 text-center text-sm text-slate-500">
                  No audit events yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
