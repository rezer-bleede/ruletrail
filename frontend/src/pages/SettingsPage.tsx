export default function SettingsPage() {
  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-presight-primary">Settings</h1>
      <p className="text-xs text-slate-500">
        Placeholder configuration for RBAC, theme preferences, and artifact retention. Future iterations will expand these
        options.
      </p>
      <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-500">
        <p className="font-semibold text-slate-600">Coming soon</p>
        <p className="mt-2 text-xs text-slate-500">
          Define user roles, connect additional rulepack registries, and manage retention policies for exports and traces.
        </p>
      </div>
    </div>
  )
}
