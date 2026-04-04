import { useAuthStore } from '@/store/authStore';
import { useDashboardStore } from '@/store/dashboardStore';
import { useSites, useLogout } from '@/api/hooks';
import { cn } from '@/utils/cn';
import { useState } from 'react';
import { useTranslation } from '@/i18n/useTranslation';
import { LANGUAGES } from '@/i18n/translations';
import type { Language } from '@/i18n/translations';

export function Header() {
  const user = useAuthStore((s) => s.user);
  const role = useAuthStore((s) => s.role);
  const {
    selectedSiteId, setSelectedSite,
    selectedYear, selectedMonth, setSelectedPeriod,
    currencyMode, toggleCurrencyMode,
    toggleTheme, theme,
    language: currentLang, setLanguage,
  } = useDashboardStore();
  const { t } = useTranslation();

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
    <header className="bg-white border-b border-slate-200 h-14 sticky top-0 z-30 flex items-center justify-between px-6">
      {/* Left: Site + Period selectors */}
      <div className="flex items-center gap-3">
        {(role === 'group_cfo' || role === 'admin') && sites && sites.length > 0 && (
          <select
            value={selectedSiteId || ''}
            onChange={(e) => setSelectedSite(e.target.value)}
            className="input h-8 w-auto px-2 text-sm"
          >
            <option value="">{t('common.consolidated')}</option>
            {sites.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        )}

        <div className="h-4 w-px bg-slate-200" />

        <div className="flex items-center gap-1.5">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedPeriod(Number(e.target.value), selectedMonth)}
            className="input h-8 w-auto px-2 text-sm"
          >
            {yearOptions.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedPeriod(selectedYear, Number(e.target.value))}
            className="input h-8 w-auto px-2 text-sm"
          >
            {months.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Right: Controls */}
      <div className="flex items-center gap-2">
        {/* Currency toggle */}
        <div className="flex rounded-lg border border-slate-300 overflow-hidden">
          {(['local', 'EUR'] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => currencyMode !== mode && toggleCurrencyMode()}
              className={cn(
                'h-7 px-3 text-xs font-medium transition-colors duration-150',
                currencyMode === mode
                  ? 'bg-brand-500 text-white'
                  : 'bg-white text-slate-600 hover:bg-slate-50'
              )}
            >
              {mode === 'local' ? t('common.local') : 'EUR'}
            </button>
          ))}
        </div>

        {/* Language selector */}
        <select
          value={currentLang}
          onChange={(e) => setLanguage(e.target.value as Language)}
          className="input h-8 w-auto px-2 text-xs"
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.flag} {lang.code.toUpperCase()}
            </option>
          ))}
        </select>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors duration-150 hover:bg-slate-100 hover:text-slate-600"
        >
          {theme === 'light' ? (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          ) : (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          )}
        </button>

        {/* User avatar + dropdown */}
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex h-8 items-center gap-2 rounded-lg px-2 transition-colors duration-150 hover:bg-slate-100"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-500 text-[11px] font-semibold text-white">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="hidden text-sm font-medium text-slate-700 sm:block">
              {user?.full_name?.split(' ')[0] || t('common.user')}
            </span>
            <svg className="h-3.5 w-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {userMenuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
              <div className="absolute right-0 z-50 mt-2 w-52 animate-scale-in overflow-hidden rounded-xl card shadow-lg">
                <div className="border-b border-slate-200 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-900">{user?.full_name}</p>
                  <p className="truncate text-xs text-slate-500 mt-0.5">{user?.email}</p>
                </div>
                <div className="py-1">
                  <button
                    onClick={() => { setUserMenuOpen(false); logout.mutate(); }}
                    className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-red-600 transition-colors duration-150 hover:bg-red-50"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                    </svg>
                    {t('common.signOut')}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
