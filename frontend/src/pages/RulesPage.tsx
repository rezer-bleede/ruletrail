import { Fragment, useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { ArrowUpTrayIcon, PlusIcon } from '@heroicons/react/24/outline'
import {
  createRule,
  deleteRule,
  fetchRules,
  importRulepacks,
  updateRule,
  useRulepacks
} from '../hooks/useRulepacks'
import { ConditionClause, Rule, RulePackSummary } from '../types'

interface RuleFormState {
  id?: number
  rule_no: string
  new_rule_name: string
  rule_logic_business?: string
  de_rule_logic?: string
  conditions: ConditionClause[]
  order_index: number
}

const emptyForm: RuleFormState = {
  rule_no: '',
  new_rule_name: '',
  rule_logic_business: '',
  de_rule_logic: '',
  conditions: [],
  order_index: 1
}

export default function RulesPage() {
  const { rulepacks, loading, refresh } = useRulepacks()
  const [selectedPack, setSelectedPack] = useState<RulePackSummary | null>(null)
  const [rules, setRules] = useState<Rule[]>([])
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [formState, setFormState] = useState<RuleFormState>(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [importError, setImportError] = useState<string | null>(null)
  const [importMessage, setImportMessage] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    if (rulepacks.length && !selectedPack) {
      setSelectedPack(rulepacks[0])
    }
  }, [rulepacks])

  useEffect(() => {
    if (selectedPack) {
      fetchRules(selectedPack.id).then(setRules)
    }
  }, [selectedPack])

  const filteredRules = useMemo(() => {
    if (!search) return rules
    return rules.filter((rule) =>
      [rule.rule_no, rule.new_rule_name, rule.rule_logic_business]
        .filter(Boolean)
        .some((value) => value!.toLowerCase().includes(search.toLowerCase()))
    )
  }, [rules, search])

  const openCreateDialog = () => {
    setFormState({ ...emptyForm, order_index: rules.length + 1 })
    setError(null)
    setDialogOpen(true)
  }

  const openEditDialog = (rule: Rule) => {
    setFormState({
      id: rule.id,
      rule_no: rule.rule_no,
      new_rule_name: rule.new_rule_name,
      rule_logic_business: rule.rule_logic_business,
      de_rule_logic: rule.de_rule_logic,
      conditions: rule.conditions,
      order_index: rule.order_index
    })
    setError(null)
    setDialogOpen(true)
  }

  const handleSubmit = async () => {
    if (!selectedPack) return
    if (!formState.rule_no || !formState.new_rule_name) {
      setError('Rule No. and New Rule Name are required')
      return
    }
    const payload = {
      ...formState,
      original_fields: [],
      aggregated_fields: []
    }
    if (formState.id) {
      const updated = await updateRule(formState.id, payload)
      setRules((prev) => prev.map((r) => (r.id === updated.id ? updated : r)))
    } else {
      const created = await createRule(selectedPack.id, payload)
      setRules((prev) => [...prev, created])
    }
    setDialogOpen(false)
  }

  const handleDelete = async (rule: Rule) => {
    await deleteRule(rule.id)
    setRules((prev) => prev.filter((r) => r.id !== rule.id))
  }

  const handleImport = async (file: File) => {
    setImportError(null)
    setImportMessage(null)
    setUploading(true)
    try {
      const imported = await importRulepacks(file)
      const updated = await refresh()
      if (imported.length) {
        const newest = imported[imported.length - 1]
        const matching = updated.find((pack) => pack.id === newest.id) ?? updated[0] ?? null
        setSelectedPack(matching)
      } else if (!selectedPack && updated.length) {
        setSelectedPack(updated[0])
      }
      setImportMessage(
        imported.length
          ? `Imported ${imported.length} rulepack${
              imported.length === 1 ? '' : 's'
            }: ${imported.map((pack) => `${pack.domain} v${pack.version}`).join(', ')}`
          : 'Excel file matched an existing rulepack set'
      )
    } catch (err: any) {
      setImportError(err.message || 'Failed to import rulepack')
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      setUploading(false)
    }
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      void handleImport(file)
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
        <div className="space-y-1">
          <h1 className="text-xl font-semibold text-presight-primary">Rules</h1>
          <p className="text-xs text-slate-500">Manage and import domain rulepacks</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <input
            ref={fileInputRef}
            id="rulepack-upload"
            type="file"
            accept=".xlsx,.xls"
            className="sr-only"
            onChange={handleFileChange}
          />
          <label
            htmlFor="rulepack-upload"
            aria-disabled={uploading}
            className={`inline-flex h-9 cursor-pointer items-center gap-2 rounded-md border border-slate-300 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 ${
              uploading ? 'pointer-events-none opacity-60' : ''
            }`}
          >
            <ArrowUpTrayIcon className="h-4 w-4" />
            {uploading ? 'Uploading…' : 'Upload Excel'}
          </label>
          <select
            className="h-9 rounded-md border border-slate-300 px-2.5 text-sm text-slate-700 disabled:opacity-60"
            value={selectedPack?.id ?? ''}
            disabled={!rulepacks.length}
            onChange={(event) => {
              const pack = rulepacks.find((rp) => rp.id === Number(event.target.value)) || null
              setSelectedPack(pack)
            }}
          >
            {rulepacks.length ? (
              rulepacks.map((pack) => (
                <option key={pack.id} value={pack.id}>
                  {pack.domain} v{pack.version}
                </option>
              ))
            ) : (
              <option value="">No rulepacks yet</option>
            )}
          </select>
          <button
            onClick={openCreateDialog}
            className="inline-flex h-9 items-center gap-2 rounded-md bg-presight-primary px-3 text-sm font-semibold text-white shadow hover:bg-presight-secondary"
          >
            <PlusIcon className="h-4 w-4" /> New Rule
          </button>
        </div>
      </div>
      {(importError || importMessage) && (
        <div
          role="status"
          className={`flex items-center gap-2 rounded-md border px-3 py-2 text-xs ${
            importError
              ? 'border-red-200 bg-red-50 text-red-600'
              : 'border-emerald-200 bg-emerald-50 text-emerald-700'
          }`}
        >
          {importError ?? importMessage}
        </div>
      )}
      <div className="rounded-xl border border-slate-200">
        <div className="flex items-center justify-between gap-2 border-b border-slate-200 bg-slate-50 px-3 py-2.5">
          <input
            placeholder="Search rules..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm"
          />
        </div>
        <div className="max-h-[520px] overflow-y-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-100 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-3 py-2.5">Rule No.</th>
                <th className="px-3 py-2.5">Name</th>
                <th className="px-3 py-2.5">Business Logic</th>
                <th className="px-3 py-2.5">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredRules.map((rule) => (
                <tr key={rule.id} className="hover:bg-slate-50">
                  <td className="px-3 py-2.5 font-medium text-slate-700">{rule.rule_no}</td>
                  <td className="px-3 py-2.5 text-slate-700">{rule.new_rule_name}</td>
                  <td className="px-3 py-2.5 text-slate-500">{rule.rule_logic_business}</td>
                  <td className="px-3 py-2.5">
                    <div className="flex items-center gap-2 text-xs">
                      <button className="text-presight-secondary" onClick={() => openEditDialog(rule)}>
                        Edit
                      </button>
                      <button className="text-presight-primary" onClick={() => handleDelete(rule)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!filteredRules.length && (
                <tr>
                  <td colSpan={4} className="px-3 py-10 text-center text-sm text-slate-400">
                    {loading ? 'Loading rules…' : 'No rules match your search.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Transition appear show={dialogOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setDialogOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/30" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-200"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-150"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-xl bg-white p-5 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title className="text-base font-semibold text-presight-primary">
                    {formState.id ? 'Edit Rule' : 'Create Rule'}
                  </Dialog.Title>
                  {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <label className="space-y-1 text-xs font-medium text-slate-600">
                      <span>Rule No.</span>
                      <input
                        value={formState.rule_no}
                        onChange={(e) => setFormState((prev) => ({ ...prev, rule_no: e.target.value }))}
                        className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
                      />
                    </label>
                    <label className="space-y-1 text-xs font-medium text-slate-600">
                      <span>New Rule Name</span>
                      <input
                        value={formState.new_rule_name}
                        onChange={(e) => setFormState((prev) => ({ ...prev, new_rule_name: e.target.value }))}
                        className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
                      />
                    </label>
                    <label className="md:col-span-2 space-y-1 text-xs font-medium text-slate-600">
                      <span>Business Logic</span>
                      <textarea
                        value={formState.rule_logic_business}
                        onChange={(e) => setFormState((prev) => ({ ...prev, rule_logic_business: e.target.value }))}
                        className="min-h-[80px] w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
                      />
                    </label>
                    <label className="md:col-span-2 space-y-1 text-xs font-medium text-slate-600">
                      <span>Conditions (comma separated e.g. field &gt; 10)</span>
                      <textarea
                        value={formState.conditions.map((c) => `${c.field} ${c.operator} ${c.value}`).join(', ')}
                        onChange={(e) =>
                          setFormState((prev) => ({
                            ...prev,
                            conditions: e.target.value
                              .split(',')
                              .map((segment) => segment.trim())
                              .filter(Boolean)
                              .map((segment) => {
                                const [field, operator, ...rest] = segment.split(' ')
                                return { field, operator, value: rest.join(' ') }
                              })
                          }))
                        }
                        className="min-h-[80px] w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
                      />
                    </label>
                  </div>
                  <div className="mt-5 flex justify-end gap-2">
                    <button
                      onClick={() => setDialogOpen(false)}
                      className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-600"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSubmit}
                      className="rounded-md bg-presight-primary px-3 py-1.5 text-sm font-semibold text-white shadow hover:bg-presight-secondary"
                    >
                      Save
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  )
}
