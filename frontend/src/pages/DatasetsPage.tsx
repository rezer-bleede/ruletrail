import { useState } from 'react'
import api from '../api/client'
import { useDatasets } from '../hooks/useDatasets'

const emptyForm = {
  name: '',
  host: '',
  index_name: '',
  query: '{"query": {"match_all": {}}}'
}

export default function DatasetsPage() {
  const { datasets, loading, refresh } = useDatasets()
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [seeding, setSeeding] = useState(false)
  const [seedMessage, setSeedMessage] = useState<string | null>(null)

  const handleSubmit = async () => {
    try {
      setError(null)
      const parsedQuery = JSON.parse(form.query)
      setSaving(true)
      await api.post('/datasets/', {
        name: form.name,
        host: form.host,
        index_name: form.index_name,
        query: parsedQuery
      })
      setForm(emptyForm)
      refresh()
    } catch (err: any) {
      setError(err.message || 'Failed to save dataset')
    } finally {
      setSaving(false)
    }
  }

  const triggerSeed = async () => {
    setSeeding(true)
    setSeedMessage(null)
    setError(null)
    try {
      const response = await api.post('/datasets/seed-demo')
      const { indexed } = response.data as { indexed: number }
      setSeedMessage(`Loaded ${indexed} demo document${indexed === 1 ? '' : 's'} into Elasticsearch`)
    } catch (err: any) {
      setError(err.message || 'Failed to load demo data')
    } finally {
      setSeeding(false)
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-presight-primary">Datasets</h1>
          <p className="text-xs text-slate-500">Configure Elasticsearch sources</p>
        </div>
        <button
          type="button"
          onClick={triggerSeed}
          disabled={seeding}
          className="inline-flex h-9 items-center rounded-md border border-slate-300 px-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100 disabled:opacity-50"
        >
          {seeding ? 'Loading demo data…' : 'Load demo data'}
        </button>
      </div>
      {(error || seedMessage) && (
        <div
          role="status"
          className={`rounded-md border px-3 py-2 text-xs ${
            error ? 'border-red-200 bg-red-50 text-red-600' : 'border-emerald-200 bg-emerald-50 text-emerald-700'
          }`}
        >
          {error ?? seedMessage}
        </div>
      )}
      <div className="grid gap-5 md:grid-cols-2">
        <div className="space-y-3 rounded-lg border border-slate-200 p-4">
          <h2 className="text-base font-semibold text-slate-700">New Dataset</h2>
          <label className="block space-y-1 text-xs font-medium text-slate-600">
            <span>Name</span>
            <input
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            />
          </label>
          <label className="block space-y-1 text-xs font-medium text-slate-600">
            <span>Host</span>
            <input
              value={form.host}
              onChange={(e) => setForm((prev) => ({ ...prev, host: e.target.value }))}
              className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            />
          </label>
          <label className="block space-y-1 text-xs font-medium text-slate-600">
            <span>Index Name</span>
            <input
              value={form.index_name}
              onChange={(e) => setForm((prev) => ({ ...prev, index_name: e.target.value }))}
              className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            />
          </label>
          <label className="block space-y-1 text-xs font-medium text-slate-600">
            <span>Query JSON</span>
            <textarea
              value={form.query}
              onChange={(e) => setForm((prev) => ({ ...prev, query: e.target.value }))}
              className="h-28 w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            />
          </label>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="rounded-md bg-presight-primary px-3 py-1.5 text-sm font-semibold text-white shadow hover:bg-presight-secondary disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save Dataset'}
          </button>
        </div>
        <div className="rounded-lg border border-slate-200">
          <div className="border-b border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-600">
            Saved datasets
          </div>
          <ul className="divide-y divide-slate-200">
            {datasets.map((dataset) => (
              <li key={dataset.id} className="space-y-1 px-4 py-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-700">{dataset.name}</span>
                  <span className="text-xs text-slate-500">{dataset.host}</span>
                </div>
                <div className="text-xs text-slate-500">Index: {dataset.index_name}</div>
              </li>
            ))}
            {!datasets.length && (
              <li className="px-4 py-6 text-center text-sm text-slate-400">
                {loading ? 'Loading datasets…' : 'No datasets yet.'}
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}
