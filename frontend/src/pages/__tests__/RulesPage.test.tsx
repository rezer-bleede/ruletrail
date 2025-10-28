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
  deleteRule: vi.fn()
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
  beforeEach(() => {
    vi.clearAllMocks()
    ;(ruleHooks.useRulepacks as unknown as Mock).mockReturnValue({ rulepacks: mockedRulepacks, loading: false, error: null })
    ;(ruleHooks.fetchRules as unknown as Mock).mockResolvedValue(mockedRules)
    ;(ruleHooks.createRule as unknown as Mock).mockResolvedValue(mockedRules[0])
    ;(ruleHooks.updateRule as unknown as Mock).mockResolvedValue(mockedRules[0])
  })

  it('renders rules table with data', async () => {
    render(
      <BrowserRouter>
        <RulesPage />
      </BrowserRouter>
    )

    await waitFor(() => expect(ruleHooks.fetchRules).toHaveBeenCalled())
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
})
