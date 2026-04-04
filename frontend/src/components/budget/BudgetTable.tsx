import { useState, useCallback } from 'react';
import { useBudget, useSaveBudget } from '@/api/hooks';
import { useDashboardStore } from '@/store/dashboardStore';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { cn } from '@/utils/cn';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export function BudgetTable() {
  const selectedSiteId = useDashboardStore((s) => s.selectedSiteId);
  const selectedYear = useDashboardStore((s) => s.selectedYear);

  const { data: entries, isLoading } = useBudget({
    siteId: selectedSiteId || '',
    year: selectedYear,
  });

  const saveBudget = useSaveBudget();
  const [editedAmounts, setEditedAmounts] = useState<Map<string, string>>(new Map());
  const [isDirty, setIsDirty] = useState(false);

  const handleAmountEdit = useCallback(
    (entryId: string, value: string) => {
      setEditedAmounts((prev) => {
        const next = new Map(prev);
        next.set(entryId, value);
        return next;
      });
      setIsDirty(true);
    },
    []
  );

  const getDisplayAmount = (entry: any): string => {
    if (editedAmounts.has(entry.id)) {
      return editedAmounts.get(entry.id)!;
    }
    return String(entry.budget_amount ?? '');
  };

  const handleSave = () => {
    if (!selectedSiteId || !entries) return;

    // Build the entries array with current amounts (including edits)
    const entriesToSave = (entries as any[]).map((entry: any) => ({
      site_id: entry.site_id,
      line_item_code: entry.line_item_code,
      period_year: entry.period_year,
      period_month: entry.period_month,
      budget_amount: editedAmounts.has(entry.id)
        ? parseFloat(editedAmounts.get(entry.id)!) || 0
        : Number(entry.budget_amount),
    }));

    saveBudget.mutate(
      { siteId: selectedSiteId, entries: entriesToSave as any },
      {
        onSuccess: () => {
          setEditedAmounts(new Map());
          setIsDirty(false);
        },
      }
    );
  };

  if (!selectedSiteId) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400">
        Select a site to view budget data
      </div>
    );
  }

  if (isLoading) {
    return <LoadingSpinner label="Loading budget data..." />;
  }

  const entryList = (entries ?? []) as any[];

  return (
    <div className="space-y-4">
      {/* Actions bar */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-500 dark:text-slate-400">
          {entryList.length} budget entries for {selectedYear}
        </div>
        <div className="flex items-center gap-3">
          {isDirty && (
            <span className="text-xs text-amber-600 dark:text-amber-400">
              Unsaved changes
            </span>
          )}
          <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              setEditedAmounts(new Map());
              setIsDirty(false);
            }}
            disabled={!isDirty}
          >
            Discard
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            disabled={!isDirty}
            loading={saveBudget.isPending}
          >
            Save Budget
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border bg-white dark:bg-slate-800 dark:border-slate-700">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-900">
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Line Item Code
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Period
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Budget Amount
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
            {entryList.map((entry: any) => (
              <tr key={entry.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                <td className="px-4 py-2 text-sm font-mono text-slate-700 dark:text-slate-300">
                  {entry.line_item_code}
                </td>
                <td className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400">
                  {entry.period_year}-{MONTHS[(entry.period_month ?? 1) - 1]}
                </td>
                <td className="px-1 py-1 text-right">
                  <input
                    type="number"
                    value={getDisplayAmount(entry)}
                    onChange={(e) => handleAmountEdit(entry.id, e.target.value)}
                    className={cn(
                      'w-36 rounded border-0 bg-transparent px-2 py-1 text-right text-sm tabular-nums',
                      'text-slate-700 dark:text-slate-300',
                      'focus:bg-brand-50 focus:outline-none focus:ring-1 focus:ring-brand-500/30 dark:focus:bg-brand-900/20',
                      'hover:bg-slate-50 dark:hover:bg-slate-700/30'
                    )}
                    step="0.01"
                  />
                </td>
              </tr>
            ))}
            {entryList.length === 0 && (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-center text-sm text-slate-400">
                  No budget entries found for this site and year.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
