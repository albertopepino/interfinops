import { useState, useMemo, useCallback, useEffect } from 'react';
import { useSites, useTargets, useSaveTargets, useSiteKPIs, useConsolidatedKPIs } from '@/api/hooks';
import { useDashboardStore } from '@/store/dashboardStore';
import { useTranslation } from '@/i18n/useTranslation';
import type { KPIResponse } from '@/types/kpi';

interface KPIDefinition {
  name: string;
  category: 'Profitability' | 'Liquidity' | 'Efficiency' | 'Leverage';
  apiCategory: 'profitability' | 'liquidity' | 'efficiency' | 'leverage';
}

const KPI_DEFINITIONS: KPIDefinition[] = [
  // Profitability
  { name: 'Revenue', category: 'Profitability', apiCategory: 'profitability' },
  { name: 'Gross Margin', category: 'Profitability', apiCategory: 'profitability' },
  { name: 'EBITDA', category: 'Profitability', apiCategory: 'profitability' },
  { name: 'EBITDA Margin', category: 'Profitability', apiCategory: 'profitability' },
  { name: 'Net Profit Margin', category: 'Profitability', apiCategory: 'profitability' },
  { name: 'Net Income', category: 'Profitability', apiCategory: 'profitability' },
  // Liquidity
  { name: 'Current Ratio', category: 'Liquidity', apiCategory: 'liquidity' },
  { name: 'Quick Ratio', category: 'Liquidity', apiCategory: 'liquidity' },
  { name: 'Cash Ratio', category: 'Liquidity', apiCategory: 'liquidity' },
  { name: 'Working Capital', category: 'Liquidity', apiCategory: 'liquidity' },
  { name: 'Cash & Bank', category: 'Liquidity', apiCategory: 'liquidity' },
  // Efficiency
  { name: 'AR Turnover', category: 'Efficiency', apiCategory: 'efficiency' },
  { name: 'Days Sales Outstanding', category: 'Efficiency', apiCategory: 'efficiency' },
  { name: 'Inventory Turnover', category: 'Efficiency', apiCategory: 'efficiency' },
  { name: 'AP Turnover', category: 'Efficiency', apiCategory: 'efficiency' },
  { name: 'Cash Conversion Cycle', category: 'Efficiency', apiCategory: 'efficiency' },
  // Leverage
  { name: 'Debt-to-Equity', category: 'Leverage', apiCategory: 'leverage' },
  { name: 'Debt-to-Assets', category: 'Leverage', apiCategory: 'leverage' },
  { name: 'Equity Ratio', category: 'Leverage', apiCategory: 'leverage' },
  { name: 'Interest Coverage', category: 'Leverage', apiCategory: 'leverage' },
];

const CATEGORIES = ['Profitability', 'Liquidity', 'Efficiency', 'Leverage'] as const;

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  Profitability: { bg: 'bg-emerald-50 dark:bg-emerald-900/20', text: 'text-emerald-700 dark:text-emerald-400', border: 'border-emerald-200 dark:border-emerald-800', dot: 'bg-emerald-500' },
  Liquidity: { bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-700 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800', dot: 'bg-blue-500' },
  Efficiency: { bg: 'bg-violet-50 dark:bg-violet-900/20', text: 'text-violet-700 dark:text-violet-400', border: 'border-violet-200 dark:border-violet-800', dot: 'bg-violet-500' },
  Leverage: { bg: 'bg-amber-50 dark:bg-amber-900/20', text: 'text-amber-700 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800', dot: 'bg-amber-500' },
};

function findKPIValue(kpis: KPIResponse | undefined, category: string, name: string): number | null {
  if (!kpis) return null;
  const cats = kpis[category as keyof Pick<KPIResponse, 'profitability' | 'liquidity' | 'efficiency' | 'leverage'>];
  if (!Array.isArray(cats)) return null;
  const item = cats.find((k) => k.name === name);
  if (!item || item.value === null) return null;
  return parseFloat(item.value);
}

function formatKPIValue(value: number | null, kpiName: string): string {
  if (value === null) return '--';
  const percentKPIs = ['Gross Margin', 'EBITDA Margin', 'Net Profit Margin', 'Equity Ratio'];
  const ratioKPIs = ['Current Ratio', 'Quick Ratio', 'Cash Ratio', 'AR Turnover', 'Inventory Turnover', 'AP Turnover', 'Debt-to-Equity', 'Debt-to-Assets', 'Interest Coverage'];
  const daysKPIs = ['Days Sales Outstanding', 'Cash Conversion Cycle'];

  if (percentKPIs.includes(kpiName)) return `${(value * 100).toFixed(1)}%`;
  if (ratioKPIs.includes(kpiName)) return value.toFixed(2);
  if (daysKPIs.includes(kpiName)) return `${value.toFixed(0)} days`;
  return value.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function getStatus(currentValue: number | null, targetValue: string): 'on-track' | 'below-target' | 'no-data' {
  if (currentValue === null || !targetValue || targetValue === '') return 'no-data';
  const target = parseFloat(targetValue);
  if (isNaN(target)) return 'no-data';
  // For simplicity, on track means current >= target (or <= for debt ratios)
  return currentValue >= target ? 'on-track' : 'below-target';
}

export function TargetsPage() {
  const { t } = useTranslation();
  const { data: sites } = useSites();
  const selectedMonth = useDashboardStore((s) => s.selectedMonth);

  const [siteId, setSiteId] = useState<string | null>(null);
  const [year, setYear] = useState(2025);
  const [targetValues, setTargetValues] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const { data: targetsData, isLoading: targetsLoading } = useTargets(siteId, year);
  const { data: siteKPIs } = useSiteKPIs(siteId || '', year, selectedMonth);
  const { data: consolidatedKPIs } = useConsolidatedKPIs(year, selectedMonth);
  const saveMutation = useSaveTargets();

  const kpiData = siteId ? siteKPIs : consolidatedKPIs;

  // Populate target values from API response
  useEffect(() => {
    if (targetsData?.items) {
      const vals: Record<string, string> = {};
      for (const item of targetsData.items) {
        vals[item.kpi_name] = String(item.target_value);
      }
      setTargetValues(vals);
    } else {
      setTargetValues({});
    }
  }, [targetsData]);

  const handleTargetChange = useCallback((kpiName: string, value: string) => {
    setTargetValues((prev) => ({ ...prev, [kpiName]: value }));
    setSaveMessage(null);
  }, []);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    setSaveMessage(null);
    try {
      const targets = Object.entries(targetValues)
        .filter(([, value]) => value !== '' && !isNaN(parseFloat(value)))
        .map(([kpiName, value]) => {
          const def = KPI_DEFINITIONS.find((d) => d.name === kpiName);
          return {
            site_id: siteId,
            kpi_name: kpiName,
            kpi_category: def?.apiCategory || 'profitability',
            target_value: parseFloat(value),
            period_year: year,
            period_month: null,
          };
        });
      await saveMutation.mutateAsync(targets);
      setSaveMessage({ type: 'success', text: t('targets.saved') });
    } catch {
      setSaveMessage({ type: 'error', text: t('targets.saveFailed') });
    } finally {
      setIsSaving(false);
    }
  }, [targetValues, siteId, year, saveMutation]);

  const kpisByCategory = useMemo(() => {
    const grouped: Record<string, KPIDefinition[]> = {};
    for (const cat of CATEGORIES) {
      grouped[cat] = KPI_DEFINITIONS.filter((k) => k.category === cat);
    }
    return grouped;
  }, []);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          {t('targets.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {t('targets.subtitle')}
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Site selector */}
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500 dark:text-slate-400">{t('common.site')}</label>
          <select
            value={siteId || ''}
            onChange={(e) => setSiteId(e.target.value || null)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300"
          >
            <option value="">{t('targets.overallAllSites')}</option>
            {sites?.map((site) => (
              <option key={site.id} value={site.id}>{site.name}</option>
            ))}
          </select>
        </div>

        {/* Year selector */}
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500 dark:text-slate-400">{t('common.year')}</label>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300"
          >
            {[2024, 2025, 2026, 2027].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        {/* Save button */}
        <div className="flex flex-col gap-1 ml-auto">
          <label className="text-xs font-medium text-transparent select-none">Action</label>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                {t('targets.saving')}
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                {t('targets.saveAll')}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Save message */}
      {saveMessage && (
        <div
          className={`rounded-lg px-4 py-3 text-sm font-medium ${
            saveMessage.type === 'success'
              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400'
              : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'
          }`}
        >
          {saveMessage.text}
        </div>
      )}

      {/* Loading state */}
      {targetsLoading ? (
        <div className="flex items-center justify-center py-16">
          <div className="flex items-center gap-3 text-slate-500">
            <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Loading targets...
          </div>
        </div>
      ) : (
        /* KPI Tables by Category */
        <div className="space-y-6">
          {CATEGORIES.map((category) => {
            const kpis = kpisByCategory[category];
            const colors = CATEGORY_COLORS[category];
            return (
              <div key={category} className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
                {/* Category Header */}
                <div className={`flex items-center gap-2 px-5 py-3 ${colors.bg} border-b ${colors.border}`}>
                  <div className={`h-2.5 w-2.5 rounded-full ${colors.dot}`} />
                  <h3 className={`text-sm font-semibold ${colors.text}`}>{category}</h3>
                  <span className="text-xs text-slate-400 dark:text-slate-500">({kpis.length} KPIs)</span>
                </div>

                {/* Table */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-100 dark:border-slate-700">
                        <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">KPI</th>
                        <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{t('targets.currentValue')}</th>
                        <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{t('targets.target')}</th>
                        <th className="px-5 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{t('targets.status')}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50 dark:divide-slate-700/50">
                      {kpis.map((kpi) => {
                        const currentValue = findKPIValue(kpiData, kpi.apiCategory, kpi.name);
                        const targetVal = targetValues[kpi.name] || '';
                        const status = getStatus(currentValue, targetVal);
                        return (
                          <tr
                            key={kpi.name}
                            className="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-700/20"
                          >
                            <td className="px-5 py-3.5">
                              <span className="text-sm font-medium text-slate-800 dark:text-slate-200">
                                {kpi.name}
                              </span>
                            </td>
                            <td className="px-5 py-3.5 text-right">
                              <span className="text-sm tabular-nums text-slate-600 dark:text-slate-400">
                                {formatKPIValue(currentValue, kpi.name)}
                              </span>
                            </td>
                            <td className="px-5 py-3.5 text-right">
                              <input
                                type="text"
                                inputMode="decimal"
                                value={targetVal}
                                onChange={(e) => handleTargetChange(kpi.name, e.target.value)}
                                placeholder="--"
                                className="w-28 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-right text-sm tabular-nums text-slate-700 shadow-sm transition-colors placeholder:text-slate-300 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-300 dark:placeholder:text-slate-600"
                              />
                            </td>
                            <td className="px-5 py-3.5">
                              <div className="flex justify-center">
                                {status === 'on-track' && (
                                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    {t('targets.onTrack')}
                                  </span>
                                )}
                                {status === 'below-target' && (
                                  <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
                                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                                    </svg>
                                    {t('targets.belowTarget')}
                                  </span>
                                )}
                                {status === 'no-data' && (
                                  <span className="inline-flex items-center gap-1 rounded-full bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-400 dark:bg-slate-700 dark:text-slate-500">
                                    --
                                  </span>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
