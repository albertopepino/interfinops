import { useDashboardStore } from '@/store/dashboardStore';
import { useUploadHistory } from '@/api/hooks';
import { UploadForm } from '@/components/upload/UploadForm';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { formatDateTime } from '@/utils/formatters';
import { useTranslation } from '@/i18n/useTranslation';

const STATUS_VARIANT: Record<string, 'positive' | 'negative' | 'neutral' | 'warning' | 'info'> = {
  validated: 'positive',
  approved: 'positive',
  pending: 'warning',
  rejected: 'negative',
};

const STATEMENT_LABELS: Record<string, string> = {
  income_statement: 'Income Statement',
  balance_sheet: 'Balance Sheet',
  cash_flow: 'Cash Flow',
};

export function UploadPage() {
  const { t } = useTranslation();
  const selectedSiteId = useDashboardStore((s) => s.selectedSiteId);
  const { data: history, isLoading: historyLoading } = useUploadHistory(selectedSiteId || '');

  return (
    <div className="space-y-8 animate-in">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight font-display text-slate-900 dark:text-white">
          {t('upload.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {t('upload.subtitle')}
        </p>
      </div>

      {/* Upload form */}
      <Card padding="lg">
        <UploadForm />
      </Card>

      {/* Upload history */}
      <div>
        <h2 className="text-lg font-semibold font-display text-slate-900 dark:text-white mb-4">
          {t('upload.history')}
        </h2>

        {historyLoading ? (
          <LoadingSpinner label="Loading history..." />
        ) : !history || history.items.length === 0 ? (
          <Card padding="lg">
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <svg className="h-12 w-12 text-slate-300 dark:text-slate-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                No uploads yet. Upload your first financial statement above.
              </p>
            </div>
          </Card>
        ) : (
          <div className="glass-card overflow-hidden">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-900">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Statement Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Period
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Uploaded By
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Uploaded At
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Items
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {history.items.map((stmt) => (
                  <tr key={stmt.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3 text-sm text-slate-700 dark:text-slate-300">
                      {STATEMENT_LABELS[stmt.statementType] || stmt.statementType}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700 dark:text-slate-300">
                      {stmt.period.label}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={STATUS_VARIANT[stmt.status] || 'neutral'}>
                        {stmt.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500 dark:text-slate-400">
                      {stmt.uploadedBy}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500 dark:text-slate-400">
                      {formatDateTime(stmt.uploadedAt)}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500 dark:text-slate-400 tabular-nums">
                      {stmt.lineItems.length}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
