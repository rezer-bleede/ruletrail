import { Route, Routes } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import RulesPage from './pages/RulesPage'
import DatasetsPage from './pages/DatasetsPage'
import RunsPage from './pages/RunsPage'
import EvaluationPage from './pages/EvaluationPage'
import SettingsPage from './pages/SettingsPage'
import ResultsPage from './pages/ResultsPage'
import ShellLayout from './components/ShellLayout'

function App() {
  return (
    <ShellLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/rules" element={<RulesPage />} />
        <Route path="/datasets" element={<DatasetsPage />} />
        <Route path="/runs" element={<RunsPage />} />
        <Route path="/start" element={<EvaluationPage />} />
        <Route path="/results/:runId" element={<ResultsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </ShellLayout>
  )
}

export default App
