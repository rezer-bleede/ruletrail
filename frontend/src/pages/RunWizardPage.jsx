import { useState } from 'react'
import { useRulepacks, useRun } from '../hooks/useRuletrail'

export default function RunWizardPage() {
  const { data: rulepacks } = useRulepacks()
  const runMutation = useRun()
  const [selectedVersion, setSelectedVersion] = useState('')
  const [indexName, setIndexName] = useState('ruletrail-demo')
  const [filters, setFilters] = useState('status=active')
  const [createdBy, setCreatedBy] = useState('demo.user@presight.ai')

  const publishedVersions = rulepacks?.flatMap((pack) => pack.versions.filter((v) => v.published)) || []

  return (
    <div className="presight-card space-y-4">
      <h2 className="text-lg font-semibold text-presightBlue">Run Wizard</h2>
      <form
        className="grid gap-4 md:grid-cols-2"
        onSubmit={(event) => {
          event.preventDefault()
          if (!selectedVersion) return
          const filtersObject = filters
            .split('&')
            .filter(Boolean)
            .reduce((acc, part) => {
              const [key, value] = part.split('=')
              if (key && value) acc[key] = value
              return acc
            }, {})
          runMutation.mutate({
            rulepack_version_id: selectedVersion,
            elasticsearch_index: indexName,
            filters: filtersObject,
            created_by: createdBy,
          })
        }}
      >
        <label className="flex flex-col gap-1 text-sm font-medium">
          Published Version
          <select
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={selectedVersion}
            onChange={(event) => setSelectedVersion(event.target.value)}
            required
          >
            <option value="">Select a version</option>
            {publishedVersions.map((version) => (
              <option key={version.id} value={version.id}>
                {version.version} — {version.metadata?.source_filename || version.source_filename}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          Elasticsearch Index
          <input
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={indexName}
            onChange={(e) => setIndexName(e.target.value)}
            required
          />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          Filters (key=value&key=value)
          <input
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={filters}
            onChange={(e) => setFilters(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          Requested By
          <input
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={createdBy}
            onChange={(e) => setCreatedBy(e.target.value)}
          />
        </label>
        <button
          type="submit"
          className="md:col-span-2 rounded-full bg-presightTeal px-4 py-2 text-sm font-semibold text-white shadow hover:bg-presightTeal/80"
          disabled={runMutation.isPending}
        >
          {runMutation.isPending ? 'Running…' : 'Start Run'}
        </button>
      </form>
      {runMutation.isSuccess && (
        <div className="rounded-md border border-presightTeal/40 bg-presightTeal/10 px-4 py-3 text-sm text-presightBlue">
          Run started. Run ID: <span className="font-mono">{runMutation.data.run_id}</span>
        </div>
      )}
      {runMutation.isError && <p className="text-sm text-red-500">{runMutation.error.message}</p>}
    </div>
  )
}
