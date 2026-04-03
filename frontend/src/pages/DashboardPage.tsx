import { useMemo, useState } from 'react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useSiteKPIs, useConsolidatedKPIs } from '@/api/hooks';
import { KPICard } from '@/components/dashboard/KPICard';
import { DashboardGrid } from '@/components/dashboard/DashboardGrid';
import { formatCurrency, formatPercent, formatRatio } from '@/utils/formatters';
import { useTranslation } from '@/i18n/useTranslation';
import type { KPIResponse, KPICardData } from '@/types/kpi';

const ALL_KPI_OPTIONS = [
  { id: 'revenue', label: 'Revenue' },
  { id: 'gross-margin', label: 'Gross Margin' },
  { id: 'ebitda', label: 'EBITDA' },
  { id: 'net-margin', label: 'Net Profit Margin' },
  { id: 'current-ratio', label: 'Current Ratio' },
  { id: 'working-capital', label: 'Working Capital' },
  { id: 'debt-equity', label: 'Debt / Equity' },
  { id: 'cash', label: 'Cash & Bank' },
];

const ALL_WIDGET_OPTIONS = [
  { id: 'revenue-trend', label: 'Revenue Trend' },
  { id: 'profitability', label: 'Profitability Margins' },
  { id: 'working-capital', label: 'Working Capital' },
  { id: 'ar-ap', label: 'AR vs AP Turnover' },
  { id: 'cash-flow', label: 'Cash & Bank Balance' },
  { id: 'expense-breakdown', label: 'Revenue Composition' },
];

function findKPI(kpis: KPIResponse, category: string, name: string): number {
  const cats = kpis[category as keyof Pick<KPIResponse, 'profitability' | 'liquidity' | 'efficiency' | 'leverage'>];
  if (!Array.isArray(cats)) return 0;
  const item = cats.find((k) => k.name === name);
  if (!item || item.value === null) return 0;
  return parseFloat(item.value);
}

export function DashboardPage() {
  const { t } = useTranslation();
  const [showCustomize, setShowCustomize] = useState(false);
  const selectedSiteId = useDashboardStore((s) => s.selectedSiteId);
  const selectedYear = useDashboardStore((s) => s.selectedYear);
  const selectedMonth = useDashboardStore((s) => s.selectedMonth);
  const currencyMode = useDashboardStore((s) => s.currencyMode);
  const visibleKPIs = useDashboardStore((s) => s.visibleKPIs);
  const visibleWidgets = useDashboardStore((s) => s.visibleWidgets);
  const setVisibleKPIs = useDashboardStore((s) => s.setVisibleKPIs);
  const setVisibleWidgets = useDashboardStore((s) => s.setVisibleWidgets);

  const { data: siteKPIs, isLoading: siteLoading } = useSiteKPIs(
    selectedSiteId || '', selectedYear, selectedMonth
  );
  const { data: consolidatedKPIs, isLoading: consolidatedLoading } = useConsolidatedKPIs(
    selectedYear, selectedMonth
  );

  const kpiData = selectedSiteId ? siteKPIs : consolidatedKPIs;
  const isLoading = selectedSiteId ? siteLoading : consolidatedLoading;
  const currency = currencyMode === 'EUR' ? 'EUR' : (kpiData?.currency || 'EUR');

  const kpiCards: KPICardData[] = useMemo(() => {
    if (!kpiData) return [];

    const revenue = findKPI(kpiData, 'profitability', 'Revenue');
    const grossMargin = findKPI(kpiData, 'profitability', 'Gross Margin');
    const ebitda = findKPI(kpiData, 'profitability', 'EBITDA');
    const netMargin = findKPI(kpiData, 'profitability', 'Net Profit Margin');
    const currentRatio = findKPI(kpiData, 'liquidity', 'Current Ratio');
    const workingCapital = findKPI(kpiData, 'liquidity', 'Working Capital');
    const debtEquity = findKPI(kpiData, 'leverage', 'Debt-to-Equity');
    const cash = findKPI(kpiData, 'liquidity', 'Cash & Bank');

    return [
      {
        id: 'revenue', label: t('kpi.revenue'), value: revenue,
        formattedValue: formatCurrency(revenue, currency, { compact: true }),
        isPositiveGood: true, unit: 'currency', icon: 'revenue', color: 'blue',
      },
      {
        id: 'gross-margin', label: t('kpi.grossMargin'), value: grossMargin * 100,
        formattedValue: formatPercent(grossMargin * 100),
        isPositiveGood: true, unit: 'percent', icon: 'profit', color: 'emerald',
      },
      {
        id: 'ebitda', label: t('kpi.ebitda'), value: ebitda,
        formattedValue: formatCurrency(ebitda, currency, { compact: true }),
        isPositiveGood: true, unit: 'currency', icon: 'cash', color: 'violet',
      },
      {
        id: 'net-margin', label: t('kpi.netProfitMargin'), value: netMargin * 100,
        formattedValue: formatPercent(netMargin * 100),
        isPositiveGood: true, unit: 'percent', icon: 'growth', color: 'pink',
      },
      {
        id: 'current-ratio', label: t('kpi.currentRatio'), value: currentRatio,
        formattedValue: formatRatio(currentRatio),
        isPositiveGood: true, unit: 'ratio', icon: 'ratio', color: 'cyan',
        benchmark: 2.0,
      },
      {
        id: 'working-capital', label: t('kpi.workingCapital'), value: workingCapital,
        formattedValue: formatCurrency(workingCapital, currency, { compact: true }),
        isPositiveGood: true, unit: 'currency', icon: 'cash', color: 'violet',
      },
      {
        id: 'debt-equity', label: t('kpi.debtEquity'), value: debtEquity,
        formattedValue: formatRatio(debtEquity),
        isPositiveGood: false, unit: 'ratio', icon: 'expense', color: 'amber',
        benchmark: 1.5,
      },
      {
        id: 'cash', label: t('kpi.cashBank'), value: cash,
        formattedValue: formatCurrency(cash, currency, { compact: true }),
        isPositiveGood: true, unit: 'currency', icon: 'revenue', color: 'blue',
      },
    ];
  }, [kpiData, currency, t]);

  const periodLabel = new Date(selectedYear, selectedMonth - 1)
    .toLocaleString('en', { month: 'long', year: 'numeric' });

  const filteredKPICards = useMemo(
    () => kpiCards.filter((kpi) => visibleKPIs.includes(kpi.id)),
    [kpiCards, visibleKPIs]
  );

  function toggleKPI(id: string) {
    setVisibleKPIs(
      visibleKPIs.includes(id)
        ? visibleKPIs.filter((k) => k !== id)
        : [...visibleKPIs, id]
    );
  }

  function toggleWidget(id: string) {
    setVisibleWidgets(
      visibleWidgets.includes(id)
        ? visibleWidgets.filter((w) => w !== id)
        : [...visibleWidgets, id]
    );
  }

  return (
    <div className="space-y-8 animate-in">
      {/* Page Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            {t('dashboard.title')}
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {selectedSiteId ? kpiData?.site_name : t('dashboard.consolidated')} &mdash; {periodLabel}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowCustomize(true)}
            className="btn-secondary"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            {t('dashboard.customize')}
          </button>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <div className="h-2 w-2 rounded-full bg-positive-500 animate-pulse-soft" />
            {t('dashboard.dataRefreshed')}
          </div>
        </div>
      </div>

      {/* Customization Modal */}
      {showCustomize && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
          onClick={() => setShowCustomize(false)}
        >
          <div
            className="mx-4 w-full max-w-lg glass-card p-6"
            style={{ animation: 'scaleIn 0.25s cubic-bezier(0.4, 0, 0.2, 1)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('dashboard.customize')}</h2>
              <button
                onClick={() => setShowCustomize(false)}
                className="rounded-xl p-1.5 text-slate-400 hover:bg-slate-100/60 hover:text-slate-600 dark:hover:bg-slate-700/50 dark:hover:text-slate-300 transition-all duration-150"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              {/* KPI Cards Section */}
              <div>
                <h3 className="label">
                  {t('dashboard.kpiCards')}
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {ALL_KPI_OPTIONS.map((kpi) => (
                    <label
                      key={kpi.id}
                      className="flex items-center gap-2.5 rounded-xl border border-slate-200/40 px-3 py-2.5 cursor-pointer transition-all duration-150 hover:bg-slate-50/60 dark:border-slate-600/30 dark:hover:bg-slate-700/40"
                    >
                      <input
                        type="checkbox"
                        checked={visibleKPIs.includes(kpi.id)}
                        onChange={() => toggleKPI(kpi.id)}
                        className="h-4 w-4 rounded-md border-slate-300 text-brand-600 focus:ring-brand-500 dark:border-slate-600 dark:bg-slate-700"
                      />
                      <span className="text-sm text-slate-700 dark:text-slate-300">{kpi.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Chart Widgets Section */}
              <div>
                <h3 className="label">
                  {t('dashboard.chartWidgets')}
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {ALL_WIDGET_OPTIONS.map((widget) => (
                    <label
                      key={widget.id}
                      className="flex items-center gap-2.5 rounded-xl border border-slate-200/40 px-3 py-2.5 cursor-pointer transition-all duration-150 hover:bg-slate-50/60 dark:border-slate-600/30 dark:hover:bg-slate-700/40"
                    >
                      <input
                        type="checkbox"
                        checked={visibleWidgets.includes(widget.id)}
                        onChange={() => toggleWidget(widget.id)}
                        className="h-4 w-4 rounded-md border-slate-300 text-brand-600 focus:ring-brand-500 dark:border-slate-600 dark:bg-slate-700"
                      />
                      <span className="text-sm text-slate-700 dark:text-slate-300">{widget.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => {
                  setVisibleKPIs(ALL_KPI_OPTIONS.map((k) => k.id));
                  setVisibleWidgets(ALL_WIDGET_OPTIONS.map((w) => w.id));
                }}
                className="btn-secondary !px-4 !py-2 !text-sm"
              >
                {t('dashboard.resetDefault')}
              </button>
              <button
                onClick={() => setShowCustomize(false)}
                className="btn-primary !px-5 !py-2 !text-sm"
              >
                {t('dashboard.done')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* KPI Summary Cards */}
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="glass-card p-5" style={{ animationDelay: `${i * 50}ms` }}>
              <div className="flex items-start gap-4">
                <div className="h-11 w-11 rounded-xl bg-slate-200/50 dark:bg-slate-700/50" style={{ animation: 'shimmer 2s linear infinite', backgroundSize: '200% 100%', backgroundImage: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)' }} />
                <div className="flex-1 space-y-3 pt-1">
                  <div className="h-3 w-16 rounded-md bg-slate-200/50 dark:bg-slate-700/50" />
                  <div className="h-7 w-24 rounded-md bg-slate-200/50 dark:bg-slate-700/50" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredKPICards.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {filteredKPICards.map((kpi, index) => (
            <KPICard key={kpi.id} data={kpi} index={index} />
          ))}
        </div>
      ) : (
        <div className="glass-card border-dashed p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-slate-300 dark:text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="mt-4 text-lg font-semibold text-slate-700 dark:text-slate-300">No financial data</h3>
          <p className="mt-1 text-sm text-slate-500">Select a period with uploaded financial statements (Jul-Dec 2025)</p>
        </div>
      )}

      {/* Chart Widgets */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-800 dark:text-slate-200">
          {t('dashboard.performanceOverview')}
        </h2>
        <DashboardGrid />
      </div>
    </div>
  );
}
