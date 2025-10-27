import { useSettings } from '../hooks/useRuletrail'

export default function SettingsPage() {
  const { data: settings } = useSettings()

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <section className="presight-card">
        <h2 className="text-lg font-semibold text-presightBlue">Platform</h2>
        {settings ? (
          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="font-semibold text-slate-500">Environment</dt>
              <dd>{settings.environment}</dd>
            </div>
            <div>
              <dt className="font-semibold text-slate-500">Elasticsearch Index</dt>
              <dd>{settings.elasticsearch_index}</dd>
            </div>
            <div>
              <dt className="font-semibold text-slate-500">AI Assist</dt>
              <dd>{settings.feature_ai_assist_enabled ? 'Enabled (toggle available)' : 'Disabled'}</dd>
            </div>
          </dl>
        ) : (
          <p className="mt-4 text-sm text-slate-500">Loading settings…</p>
        )}
      </section>

      <section className="presight-card">
        <h2 className="text-lg font-semibold text-presightBlue">Branding</h2>
        <p className="mt-2 text-sm text-slate-600">
          RuleTrail ships with Presight.ai inspired visuals out of the box. Future releases will let you upload logos and customize
          accent colors per tenant.
        </p>
        <div className="mt-4 flex gap-3">
          <div className="h-16 w-16 rounded-lg bg-presightBlue" />
          <div className="h-16 w-16 rounded-lg bg-presightTeal" />
          <div className="h-16 w-16 rounded-lg bg-slate-900" />
        </div>
      </section>
    </div>
  )
}
