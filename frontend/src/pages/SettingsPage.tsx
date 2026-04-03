import { useAuthStore } from '@/store/authStore';
import { useDashboardStore } from '@/store/dashboardStore';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { useTranslation } from '@/i18n/useTranslation';

export function SettingsPage() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const { theme, setTheme, currencyMode, setCurrencyMode } = useDashboardStore();

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          {t('settings.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {t('settings.subtitle')}
        </p>
      </div>

      {/* Profile section */}
      <Card>
        <CardHeader>
          <CardTitle>{t('settings.profile')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-600 text-xl font-bold text-white">
                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div>
                <div className="text-lg font-semibold text-slate-900 dark:text-white">
                  {user?.full_name || 'User'}
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400">
                  {user?.email || 'user@example.com'}
                </div>
                <Badge variant="info" size="sm" className="mt-1">
                  {user?.role?.replace('_', ' ').toUpperCase() || 'ROLE'}
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 pt-4 border-t dark:border-slate-700">
              <div>
                <label className="label">{t('settings.fullName')}</label>
                <input
                  type="text"
                  className="input-base"
                  value={user?.full_name || ''}
                  readOnly
                />
              </div>
              <div>
                <label className="label">{t('settings.email')}</label>
                <input
                  type="email"
                  className="input-base"
                  value={user?.email || ''}
                  readOnly
                />
              </div>
            </div>

            {user?.assigned_site_ids && user.assigned_site_ids.length > 0 && (
              <div className="pt-4 border-t dark:border-slate-700">
                <label className="label">Assigned Sites</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {user.assigned_site_ids.map((siteId: string) => (
                    <Badge key={siteId} variant="neutral">
                      {siteId}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Dashboard Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Dashboard Preferences</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label={t('settings.theme')}
                options={[
                  { value: 'light', label: 'Light' },
                  { value: 'dark', label: 'Dark' },
                ]}
                value={theme}
                onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
              />
              <Select
                label={t('settings.currency')}
                options={[
                  { value: 'EUR', label: 'EUR (Group Currency)' },
                  { value: 'local', label: 'Local Currency' },
                ]}
                value={currencyMode}
                onChange={(e) => setCurrencyMode(e.target.value as 'EUR' | 'local')}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Authentication is managed via secure HTTP-only cookies. No sensitive tokens
              are stored in your browser's local storage.
            </p>
            <Button variant="secondary" size="sm">
              Change Password
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
