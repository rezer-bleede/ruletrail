export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-presight-primary">Settings</h1>
      <p className="text-sm text-slate-500">
        Placeholder configuration for RBAC, theme preferences, and artifact retention. Future iterations will expand these
        options.
      </p>
      <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-500">
        <p className="font-semibold text-slate-600">Coming soon</p>
        <p className="mt-2">
          Define user roles, connect additional rulepack registries, and manage retention policies for exports and traces.
        </p>
      </div>
    </div>
  )
}
