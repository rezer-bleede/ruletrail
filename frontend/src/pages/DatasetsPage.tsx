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

  const handleSubmit = async () => {
    try {
      const parsedQuery = JSON.parse(form.query)
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
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-presight-primary">Datasets</h1>
          <p className="text-sm text-slate-500">Configure Elasticsearch sources</p>
        </div>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4 rounded-xl border border-slate-200 p-5">
          <h2 className="text-lg font-semibold text-slate-700">New Dataset</h2>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <label className="block space-y-1 text-sm text-slate-600">
            <span>Name</span>
            <input
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>
          <label className="block space-y-1 text-sm text-slate-600">
            <span>Host</span>
            <input
              value={form.host}
              onChange={(e) => setForm((prev) => ({ ...prev, host: e.target.value }))}
              className="w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>
          <label className="block space-y-1 text-sm text-slate-600">
            <span>Index Name</span>
            <input
              value={form.index_name}
              onChange={(e) => setForm((prev) => ({ ...prev, index_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>
          <label className="block space-y-1 text-sm text-slate-600">
            <span>Query JSON</span>
            <textarea
              value={form.query}
              onChange={(e) => setForm((prev) => ({ ...prev, query: e.target.value }))}
              className="h-32 w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>
          <button
            onClick={handleSubmit}
            className="rounded-lg bg-presight-primary px-4 py-2 text-sm font-semibold text-white shadow hover:bg-presight-secondary"
          >
            Save Dataset
          </button>
        </div>
        <div className="rounded-xl border border-slate-200">
          <div className="border-b border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-600">Saved datasets</div>
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
