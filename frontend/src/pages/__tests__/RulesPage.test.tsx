import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, type Mock } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import RulesPage from '../../pages/RulesPage'
import * as ruleHooks from '../../hooks/useRulepacks'
import { Rule, RulePackSummary } from '../../types'

vi.mock('../../hooks/useRulepacks', () => ({
  useRulepacks: vi.fn(),
  fetchRules: vi.fn(),
  createRule: vi.fn(),
  updateRule: vi.fn(),
  deleteRule: vi.fn(),
  importRulepacks: vi.fn()
}))

const mockedRulepacks: RulePackSummary[] = [
  { id: 1, domain: 'HR', version: 1, checksum: 'abc', uploaded_at: new Date().toISOString() }
]

const mockedRules: Rule[] = [
  {
    id: 10,
    rule_no: 'HR-001',
    new_rule_name: 'Test Rule',
    order_index: 1,
    conditions: [],
    original_fields: [],
    aggregated_fields: [],
    rule_logic_business: 'Test logic'
  }
]

describe('RulesPage', () => {
  const refreshMock = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    refreshMock.mockResolvedValue(mockedRulepacks)
    ;(ruleHooks.useRulepacks as unknown as Mock).mockReturnValue({
      rulepacks: mockedRulepacks,
      loading: false,
      error: null,
      refresh: refreshMock
    })
    ;(ruleHooks.fetchRules as unknown as Mock).mockResolvedValue(mockedRules)
    ;(ruleHooks.createRule as unknown as Mock).mockResolvedValue(mockedRules[0])
    ;(ruleHooks.updateRule as unknown as Mock).mockResolvedValue(mockedRules[0])
    ;(ruleHooks.importRulepacks as unknown as Mock).mockResolvedValue(mockedRulepacks)
  })

  it('renders rules table with data', async () => {
    render(
      <BrowserRouter>
        <RulesPage />
      </BrowserRouter>
    )

    await waitFor(() => expect(ruleHooks.fetchRules).toHaveBeenCalled())
    refreshMock.mockClear()
    expect(await screen.findByText('Test Rule')).toBeInTheDocument()
  })

  it('validates required fields before submitting a new rule', async () => {
    render(
      <BrowserRouter>
        <RulesPage />
      </BrowserRouter>
    )

    await waitFor(() => expect(ruleHooks.fetchRules).toHaveBeenCalled())

    await userEvent.click(screen.getByRole('button', { name: /new rule/i }))
    await userEvent.click(screen.getByRole('button', { name: /save/i }))

    expect(await screen.findByText('Rule No. and New Rule Name are required')).toBeInTheDocument()
    expect(ruleHooks.createRule).not.toHaveBeenCalled()
  })

  it('imports rulepacks through excel upload', async () => {
    const newPack: RulePackSummary = {
      id: 2,
      domain: 'Finance',
      version: 3,
      checksum: 'def',
      uploaded_at: new Date().toISOString()
    }
    ;(ruleHooks.importRulepacks as unknown as Mock).mockResolvedValue([newPack])
    refreshMock.mockResolvedValue([...mockedRulepacks, newPack])

    render(
      <BrowserRouter>
        <RulesPage />
      </BrowserRouter>
    )

    await waitFor(() => expect(ruleHooks.fetchRules).toHaveBeenCalled())

    const input = screen.getByLabelText(/upload excel/i)
    const file = new File(['content'], 'rulepack.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    await userEvent.upload(input, file)

    await waitFor(() => expect(ruleHooks.importRulepacks).toHaveBeenCalledWith(file))
    await waitFor(() => expect(refreshMock).toHaveBeenCalledTimes(1))
    expect(screen.getByRole('status')).toHaveTextContent('Imported 1 rulepack')
  })

  it('displays import errors returned by the backend', async () => {
    const error = new Error('Unable to parse conditions in sheet \"HR\" row 1: amount ~~ 10')
    ;(ruleHooks.importRulepacks as unknown as Mock).mockRejectedValue(error)

    render(
      <BrowserRouter>
        <RulesPage />
      </BrowserRouter>
    )

    await waitFor(() => expect(ruleHooks.fetchRules).toHaveBeenCalled())

    const input = screen.getByLabelText(/upload excel/i)
    const file = new File(['content'], 'invalid.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    await userEvent.upload(input, file)

    await waitFor(() => expect(ruleHooks.importRulepacks).toHaveBeenCalledWith(file))
    expect(await screen.findByRole('status')).toHaveTextContent('Unable to parse conditions')
  })
})
