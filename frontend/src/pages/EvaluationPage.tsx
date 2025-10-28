import { useEffect, useState } from 'react'
import api from '../api/client'
import { useRulepacks } from '../hooks/useRulepacks'
import { useDatasets } from '../hooks/useDatasets'
import { useNavigate } from 'react-router-dom'

const steps = ['Select Domain', 'Choose Rulepack', 'Choose Dataset', 'Review & Run']

export default function EvaluationPage() {
  const navigate = useNavigate()
  const { rulepacks } = useRulepacks()
  const { datasets } = useDatasets()
  const [step, setStep] = useState(0)
  const [domain, setDomain] = useState('')
  const [rulepackId, setRulepackId] = useState<number | null>(null)
  const [datasetId, setDatasetId] = useState<number | null>(null)
  const [running, setRunning] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    if (rulepacks.length) {
      setDomain(rulepacks[0].domain)
      setRulepackId(rulepacks[0].id)
    }
    if (datasets.length) {
      setDatasetId(datasets[0].id)
    }
  }, [rulepacks, datasets])

  const canProceed = () => {
    if (step === 0) return Boolean(domain)
    if (step === 1) return rulepackId !== null
    if (step === 2) return datasetId !== null
    return true
  }

  const runEvaluation = async () => {
    if (!domain || !rulepackId || !datasetId) return
    setRunning(true)
    try {
      const response = await api.post('/runs/start', {
        domain,
        rulepack_id: rulepackId,
        dataset_id: datasetId
      })
      setMessage('Run started successfully.')
      navigate(`/results/${response.data.id}`)
    } catch (error: any) {
      setMessage(error.message || 'Failed to start run')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-presight-primary">Start Evaluation</h1>
        <p className="text-sm text-slate-500">A guided wizard to launch a new run</p>
      </div>
      <ol className="flex items-center gap-3 text-sm">
        {steps.map((label, index) => (
          <li key={label} className={`flex items-center gap-2 ${index === step ? 'text-presight-primary' : 'text-slate-400'}`}>
            <span className={`flex h-7 w-7 items-center justify-center rounded-full border ${index <= step ? 'border-presight-primary bg-presight-primary text-white' : 'border-slate-300'}`}>
              {index + 1}
            </span>
            {label}
          </li>
        ))}
      </ol>
      <div className="rounded-xl border border-slate-200 p-6">
        {step === 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-700">Choose Domain</h2>
            <select
              className="w-full rounded-lg border border-slate-200 px-3 py-2"
              value={domain}
              onChange={(event) => setDomain(event.target.value)}
            >
              {Array.from(new Set(rulepacks.map((pack) => pack.domain))).map((domainOption) => (
                <option key={domainOption} value={domainOption}>
                  {domainOption}
                </option>
              ))}
            </select>
          </div>
        )}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-700">Select Rulepack</h2>
            <select
              className="w-full rounded-lg border border-slate-200 px-3 py-2"
              value={rulepackId ?? ''}
              onChange={(event) => setRulepackId(Number(event.target.value))}
            >
              {rulepacks
                .filter((pack) => pack.domain === domain)
                .map((pack) => (
                  <option key={pack.id} value={pack.id}>
                    v{pack.version} • {new Date(pack.uploaded_at).toLocaleString()}
                  </option>
                ))}
            </select>
          </div>
        )}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-700">Select Dataset</h2>
            <select
              className="w-full rounded-lg border border-slate-200 px-3 py-2"
              value={datasetId ?? ''}
              onChange={(event) => setDatasetId(Number(event.target.value))}
            >
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.index_name})
                </option>
              ))}
            </select>
          </div>
        )}
        {step === 3 && (
          <div className="space-y-4 text-sm text-slate-600">
            <p>Domain: <span className="font-semibold text-presight-primary">{domain}</span></p>
            <p>Rulepack: <span className="font-semibold text-presight-primary">{rulepackId}</span></p>
            <p>Dataset: <span className="font-semibold text-presight-primary">{datasetId}</span></p>
            {message && <p className="text-sm text-red-500">{message}</p>}
          </div>
        )}
        <div className="mt-6 flex justify-between">
          <button
            disabled={step === 0}
            onClick={() => setStep((prev) => Math.max(prev - 1, 0))}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 disabled:opacity-40"
          >
            Back
          </button>
          {step < steps.length - 1 ? (
            <button
              disabled={!canProceed()}
              onClick={() => setStep((prev) => prev + 1)}
              className="rounded-lg bg-presight-primary px-4 py-2 text-sm font-semibold text-white shadow disabled:opacity-40"
            >
              Next
            </button>
          ) : (
            <button
              disabled={running}
              onClick={runEvaluation}
              className="rounded-lg bg-presight-primary px-4 py-2 text-sm font-semibold text-white shadow disabled:opacity-40"
            >
              {running ? 'Running…' : 'Start Run'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
