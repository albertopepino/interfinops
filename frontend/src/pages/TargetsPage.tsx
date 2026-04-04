import { useState, useMemo, useCallback, useEffect } from 'react';
import { useSites, useTargets, useSaveTargets, useSiteKPIs, useConsolidatedKPIs } from '@/api/hooks';
import { useDashboardStore } from '@/store/dashboardStore';
import { useTranslation } from '@/i18n/useTranslation';
import { cn } from '@/utils/cn';
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
  }, [targetValues, siteId, year, saveMutation, t]);

  const kpisByCategory = useMemo(() => {
    const grouped: Record<string, KPIDefinition[]> = {};
    for (const cat of CATEGORIES) {
      grouped[cat] = KPI_DEFINITIONS.filter((k) => k.category === cat);
    }
    return grouped;
  }, []);

  // Compute stats
  const stats = useMemo(() => {
    let totalTracked = 0;
    let onTrack = 0;
    let belowTarget = 0;
    for (const kpi of KPI_DEFINITIONS) {
      const currentValue = findKPIValue(kpiData, kpi.apiCategory, kpi.name);
      const targetVal = targetValues[kpi.name] || '';
      const status = getStatus(currentValue, targetVal);
      if (status !== 'no-data') {
        totalTracked++;
        if (status === 'on-track') onTrack++;
        if (status === 'below-target') belowTarget++;
      }
    }
    return { totalTracked, onTrack, belowTarget };
  }, [kpiData, targetValues]);

  return (
    <div className="page-enter space-y-6">
      {/* ── Page Header ───────────────────────────────────────────────── */}
      <div>
        <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
          {t('targets.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {t('targets.subtitle')}
        </p>
      </div>

      {/* ── Controls row ──────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-end gap-4">
        <div className="flex flex-col gap-1">
          <label className="input-label">Site</label>
          <select
            value={siteId || ''}
            onChange={(e) => setSiteId(e.target.value || null)}
            className="input"
          >
            <option value="">{t('targets.overallAllSites')}</option>
            {sites?.map((site) => (
              <option key={site.id} value={site.id}>{site.name}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="input-label">Year</label>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="input"
          >
            {[2024, 2025, 2026, 2027].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn-primary"
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

      {/* ── Stats Row (3 white cards) ─────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            KPIs Tracked
          </p>
          <p className="mt-2 font-mono tabular-nums text-2xl font-semibold text-slate-900 dark:text-white">
            {stats.totalTracked}
          </p>
          <p className="mt-0.5 text-xs text-slate-400">of {KPI_DEFINITIONS.length} defined</p>
        </div>

        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600 dark:text-emerald-400">
            {t('targets.onTrack')}
          </p>
          <p className="mt-2 font-mono tabular-nums text-2xl font-semibold text-emerald-600 dark:text-emerald-400">
            {stats.onTrack}
          </p>
        </div>

        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-red-600 dark:text-red-400">
            {t('targets.belowTarget')}
          </p>
          <p className="mt-2 font-mono tabular-nums text-2xl font-semibold text-red-600 dark:text-red-400">
            {stats.belowTarget}
          </p>
        </div>
      </div>

      {/* ── Save message toast ──────────────────────────────────────────── */}
      {saveMessage && (
        <div
          className={cn(
            'rounded-xl px-5 py-3.5 text-sm font-medium',
            saveMessage.type === 'success'
              ? 'border border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-400'
              : 'border border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400'
          )}
        >
          {saveMessage.text}
        </div>
      )}

      {/* ── Loading state ───────────────────────────────────────────────── */}
      {targetsLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3 text-slate-400">
            <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="text-sm">Loading targets...</span>
          </div>
        </div>
      ) : (
        /* ── Category Sections ─────────────────────────────────────── */
        <div className="space-y-6">
          {CATEGORIES.map((category) => {
            const kpis = kpisByCategory[category];
            return (
              <div key={category} className="card overflow-hidden">
                {/* Section header */}
                <div className="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500 px-6 py-3 border-b border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:text-slate-400">
                  {category} ({kpis.length} KPIs)
                </div>

                {/* Table */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-100 dark:border-slate-700/50">
                        <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                          KPI
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-semibold uppercase tracking-wide text-slate-500">
                          {t('targets.currentValue')}
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-semibold uppercase tracking-wide text-slate-500">
                          {t('targets.target')}
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-semibold uppercase tracking-wide text-slate-500">
                          {t('targets.status')}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {kpis.map((kpi) => {
                        const currentValue = findKPIValue(kpiData, kpi.apiCategory, kpi.name);
                        const targetVal = targetValues[kpi.name] || '';
                        const status = getStatus(currentValue, targetVal);
                        return (
                          <tr
                            key={kpi.name}
                            className="border-b border-slate-50 transition-colors hover:bg-slate-50 dark:border-slate-700/30 dark:hover:bg-slate-700/20"
                          >
                            <td className="px-6 py-3">
                              <span className="text-sm font-medium text-slate-800 dark:text-slate-200">
                                {kpi.name}
                              </span>
                            </td>

                            <td className="px-6 py-3 text-center">
                              <span className="font-mono text-sm tabular-nums text-slate-600 dark:text-slate-400">
                                {formatKPIValue(currentValue, kpi.name)}
                              </span>
                            </td>

                            <td className="px-6 py-3 text-center">
                              <input
                                type="text"
                                inputMode="decimal"
                                value={targetVal}
                                onChange={(e) => handleTargetChange(kpi.name, e.target.value)}
                                placeholder="--"
                                className="input mx-auto block w-28 text-center font-mono tabular-nums"
                              />
                            </td>

                            <td className="px-6 py-3 text-center">
                              {status === 'on-track' && (
                                <span className="pill-green">
                                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                                  </svg>
                                  {t('targets.onTrack')}
                                </span>
                              )}
                              {status === 'below-target' && (
                                <span className="pill-red">
                                  <span className="dot" />
                                  {t('targets.belowTarget')}
                                </span>
                              )}
                              {status === 'no-data' && (
                                <span className="pill-slate">
                                  <span className="dot" />
                                  --
                                </span>
                              )}
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
