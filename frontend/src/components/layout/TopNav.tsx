import { NavLink } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useDashboardStore } from '@/store/dashboardStore';
import { useSites, useLogout } from '@/api/hooks';
import { cn } from '@/utils/cn';
import { useState } from 'react';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { label: 'Statements', path: '/statements', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { label: 'Targets', path: '/targets', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
  { label: 'Upload', path: '/upload', icon: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12' },
  { label: 'Budget', path: '/budget', icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z' },
  { label: 'Settings', path: '/settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' },
];

export function TopNav() {
  const user = useAuthStore((s) => s.user);
  const role = useAuthStore((s) => s.role);
  const {
    selectedSiteId, setSelectedSite,
    selectedYear, selectedMonth, setSelectedPeriod,
    currencyMode, toggleCurrencyMode,
    toggleTheme, theme,
  } = useDashboardStore();

  const { data: sites } = useSites();
  const logout = useLogout();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - i);
  const months = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: new Date(2000, i).toLocaleString('en', { month: 'short' }),
  }));

  return (
    <header className="glass sticky top-0 z-30 border-b border-white/10">
      {/* Top row: logo + selectors + user */}
      <div className="flex h-14 items-center justify-between px-6">
        {/* Left: Logo + Site/Period */}
        <div className="flex items-center gap-6">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 text-xs font-bold text-white shadow-lg shadow-blue-500/25">
              IF
            </div>
            <span className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">
              InterFinOps
            </span>
          </div>

          {/* Divider */}
          <div className="h-5 w-px bg-slate-200/60 dark:bg-slate-700/60" />

          {/* Site selector */}
          {(role === 'group_cfo' || role === 'admin') && sites && sites.length > 0 && (
            <select
              value={selectedSiteId || ''}
              onChange={(e) => setSelectedSite(e.target.value)}
              className="rounded-lg border-0 bg-slate-100/60 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200/60 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:bg-slate-700/40 dark:text-slate-300 dark:hover:bg-slate-600/40"
            >
              <option value="">All Sites</option>
              {sites.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          )}

          {/* Period selectors */}
          <div className="flex items-center gap-1.5">
            <select
              value={selectedYear}
              onChange={(e) => setSelectedPeriod(Number(e.target.value), selectedMonth)}
              className="rounded-lg border-0 bg-slate-100/60 px-2.5 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200/60 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:bg-slate-700/40 dark:text-slate-300"
            >
              {yearOptions.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedPeriod(selectedYear, Number(e.target.value))}
              className="rounded-lg border-0 bg-slate-100/60 px-2.5 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200/60 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:bg-slate-700/40 dark:text-slate-300"
            >
              {months.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Right: Currency toggle + Theme + User */}
        <div className="flex items-center gap-3">
          {/* Currency toggle */}
          <div className="flex items-center rounded-lg bg-slate-100/60 p-0.5 dark:bg-slate-700/40">
            <button
              onClick={() => currencyMode !== 'local' && toggleCurrencyMode()}
              className={cn(
                'rounded-md px-2.5 py-1 text-xs font-semibold transition-all duration-200',
                currencyMode === 'local'
                  ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-600 dark:text-white'
                  : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'
              )}
            >
              Local
            </button>
            <button
              onClick={() => currencyMode !== 'EUR' && toggleCurrencyMode()}
              className={cn(
                'rounded-md px-2.5 py-1 text-xs font-semibold transition-all duration-200',
                currencyMode === 'EUR'
                  ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-600 dark:text-white'
                  : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'
              )}
            >
              EUR
            </button>
          </div>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100/60 hover:text-slate-600 dark:hover:bg-slate-700/40 dark:hover:text-slate-300"
          >
            {theme === 'light' ? (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            ) : (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </button>

          {/* User */}
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-slate-100/60 dark:hover:bg-slate-700/40"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-[11px] font-semibold text-white">
                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="hidden text-sm font-medium text-slate-700 dark:text-slate-300 sm:block">
                {user?.full_name || 'User'}
              </span>
            </button>

            {userMenuOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                <div className="absolute right-0 z-50 mt-2 w-48 glass-card overflow-hidden p-0">
                  <div className="border-b border-slate-200/30 px-4 py-3 dark:border-slate-600/30">
                    <p className="truncate text-xs text-slate-500">{user?.email}</p>
                  </div>
                  <div className="py-1">
                    <button
                      onClick={() => { setUserMenuOpen(false); logout.mutate(); }}
                      className="block w-full px-4 py-2.5 text-left text-sm text-red-600 transition-colors hover:bg-red-50/50 dark:text-red-400 dark:hover:bg-red-900/10"
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Bottom row: Navigation tabs */}
      <div className="flex items-center gap-1 px-6 pb-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                  : 'text-slate-500 hover:bg-slate-100/60 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700/30 dark:hover:text-slate-300'
              )
            }
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} />
            </svg>
            {item.label}
          </NavLink>
        ))}
      </div>
    </header>
  );
}
