import { useAuthStore } from '@/store/authStore';
import { useDashboardStore } from '@/store/dashboardStore';
import { useTranslation } from '@/i18n/useTranslation';

export function SettingsPage() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const { theme, setTheme, currencyMode, setCurrencyMode } = useDashboardStore();

  const initial = user?.full_name?.charAt(0).toUpperCase() || 'U';

  return (
    <div className="page-enter space-y-6 max-w-3xl">
      {/* Page header */}
      <div>
        <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
          {t('settings.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {t('settings.subtitle')}
        </p>
      </div>

      {/* Profile section */}
      <div className="card overflow-hidden">
        <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">{t('settings.profile')}</h2>
        </div>
        <div className="p-6 space-y-6">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-200 text-xl font-bold text-slate-600 dark:bg-slate-700 dark:text-slate-300">
              {initial}
            </div>
            <div>
              <div className="text-lg font-semibold text-slate-900 dark:text-white">
                {user?.full_name || 'User'}
              </div>
              <div className="text-sm text-slate-500 dark:text-slate-400">
                {user?.email || 'user@example.com'}
              </div>
              <span className="pill-violet mt-1 inline-block">
                {user?.role?.replace('_', ' ').toUpperCase() || 'ROLE'}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 pt-4 border-t border-slate-200 dark:border-slate-700">
            <div>
              <label className="input-label">{t('settings.fullName')}</label>
              <input
                type="text"
                className="input"
                value={user?.full_name || ''}
                readOnly
              />
            </div>
            <div>
              <label className="input-label">{t('settings.email')}</label>
              <input
                type="email"
                className="input"
                value={user?.email || ''}
                readOnly
              />
            </div>
          </div>

          {user?.assigned_site_ids && user.assigned_site_ids.length > 0 && (
            <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
              <label className="input-label">Assigned Sites</label>
              <div className="flex flex-wrap gap-2 mt-2">
                {user.assigned_site_ids.map((siteId: string) => (
                  <span key={siteId} className="pill-slate">{siteId}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dashboard Preferences */}
      <div className="card overflow-hidden">
        <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">Dashboard Preferences</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="input-label">{t('settings.theme')}</label>
              <select
                className="input"
                value={theme}
                onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
            <div>
              <label className="input-label">{t('settings.currency')}</label>
              <select
                className="input"
                value={currencyMode}
                onChange={(e) => setCurrencyMode(e.target.value as 'EUR' | 'local')}
              >
                <option value="EUR">EUR (Group Currency)</option>
                <option value="local">Local Currency</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="card overflow-hidden">
        <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">Security</h2>
        </div>
        <div className="p-6 space-y-4">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Authentication is managed via secure HTTP-only cookies. No sensitive tokens
            are stored in your browser's local storage.
          </p>
          <button className="btn-primary">
            Change Password
          </button>
        </div>
      </div>
    </div>
  );
}
