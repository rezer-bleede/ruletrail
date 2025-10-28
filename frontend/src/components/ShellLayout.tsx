import { NavLink } from 'react-router-dom'
import { Fragment, ReactNode, useState } from 'react'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import { Dialog, Transition } from '@headlessui/react'

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
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const renderNavigation = () => (
    <nav className="mt-6 space-y-1">
      {navigation.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-presight-primary/10 text-presight-primary'
                : 'text-slate-600 hover:bg-presight-surface hover:text-presight-primary'
            }`
          }
          onClick={() => setSidebarOpen(false)}
        >
          <span>{item.name}</span>
        </NavLink>
      ))}
    </nav>
  )

  return (
    <div className="min-h-screen bg-presight-surface text-slate-900">
      <Transition show={sidebarOpen} as={Fragment}>
        <Dialog as="div" className="relative z-40 md:hidden" onClose={setSidebarOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-200"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/40" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-200 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-200 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative flex w-64 flex-1 flex-col bg-white p-6 shadow-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-lg font-semibold text-presight-primary">RuleTrail</p>
                    <p className="text-xs text-slate-500">Presight.ai Intelligence</p>
                  </div>
                  <button
                    type="button"
                    className="rounded-md p-1 text-slate-500 hover:text-presight-primary"
                    onClick={() => setSidebarOpen(false)}
                  >
                    <span className="sr-only">Close sidebar</span>
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
                {renderNavigation()}
              </Dialog.Panel>
            </Transition.Child>
            <div className="w-16" aria-hidden="true" />
          </div>
        </Dialog>
      </Transition>

      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white px-6 py-8 md:flex md:flex-col">
          <div>
            <p className="text-xl font-semibold text-presight-primary">RuleTrail</p>
            <p className="text-xs text-slate-500">Presight.ai Intelligence</p>
          </div>
          {renderNavigation()}
          <div className="mt-auto text-xs text-slate-400">
            <p>Fewer clicks, sharper insights.</p>
          </div>
        </aside>

        <div className="flex flex-1 flex-col">
          <header className="flex h-14 items-center gap-3 border-b border-slate-200 bg-white px-4 shadow-sm md:hidden">
            <button
              type="button"
              className="rounded-md border border-slate-200 p-2 text-slate-600"
              onClick={() => setSidebarOpen(true)}
            >
              <span className="sr-only">Open sidebar</span>
              <Bars3Icon className="h-5 w-5" />
            </button>
            <div>
              <p className="text-base font-semibold text-presight-primary">RuleTrail</p>
              <p className="text-xs text-slate-500">Presight.ai Intelligence</p>
            </div>
          </header>
          <main className="flex-1 overflow-y-auto">
            <div className="mx-auto w-full max-w-6xl px-4 py-5 sm:px-6 md:px-8 md:py-8">
              <div className="rounded-lg bg-white p-5 shadow ring-1 ring-black/5 md:rounded-xl md:p-6">
                {children}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
