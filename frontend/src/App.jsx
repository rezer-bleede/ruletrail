import { NavLink, Route, Routes } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import RulepacksPage from './pages/RulepacksPage'
import RunWizardPage from './pages/RunWizardPage'
import ResultsExplorerPage from './pages/ResultsExplorerPage'
import SettingsPage from './pages/SettingsPage'
import AuditPage from './pages/AuditPage'

const menu = [
  { name: 'Dashboard', path: '/' },
  { name: 'Rulepacks', path: '/rulepacks' },
  { name: 'Run Wizard', path: '/run' },
  { name: 'Results Explorer', path: '/results' },
  { name: 'Settings', path: '/settings' },
  { name: 'Audit', path: '/audit' },
]

export default function App() {
  return (
    <div className="min-h-screen bg-presightGray">
      <header className="bg-presightBlue text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-wide">RuleTrail</h1>
            <p className="text-sm text-slate-100">Explainability for ADAA &amp; UAEAA compliance</p>
          </div>
          <nav className="flex gap-4 text-sm">
            {menu.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `rounded-full px-4 py-2 transition ${isActive ? 'bg-presightTeal text-presightBlue' : 'hover:bg-presightTeal/20'}`
                }
              >
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/rulepacks" element={<RulepacksPage />} />
          <Route path="/run" element={<RunWizardPage />} />
          <Route path="/results" element={<ResultsExplorerPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/audit" element={<AuditPage />} />
        </Routes>
      </main>
    </div>
  )
}
