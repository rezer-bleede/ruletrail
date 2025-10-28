import { NavLink } from 'react-router-dom'
import { ReactNode } from 'react'
import { Bars3Icon } from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', to: '/' },
  { name: 'Runs', to: '/runs' },
  { name: 'Rules', to: '/rules' },
  { name: 'Datasets', to: '/datasets' },
  { name: 'Start Evaluation', to: '/start' },
  { name: 'Settings', to: '/settings' }
]

interface ShellLayoutProps {
  children: ReactNode
}

export default function ShellLayout({ children }: ShellLayoutProps) {
  return (
    <div className="min-h-screen bg-presight-surface text-slate-900">
      <div className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <Bars3Icon className="h-6 w-6 text-presight-primary" />
          <div>
            <p className="text-lg font-semibold text-presight-primary">RuleTrail</p>
            <p className="text-xs text-slate-500">Presight.ai Intelligence</p>
          </div>
        </div>
        <nav className="hidden items-center gap-4 md:flex">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-presight-primary text-white shadow'
                    : 'text-slate-600 hover:bg-presight-surface hover:text-presight-primary'
                }`
              }
            >
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>
      <main className="mx-auto max-w-7xl p-6">
        <div className="rounded-xl bg-white p-6 shadow-lg ring-1 ring-black/5">
          {children}
        </div>
      </main>
    </div>
  )
}
