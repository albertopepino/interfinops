import { useState, useMemo } from 'react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useSites, useBankAccounts, useCashPosition, useDebtMaturity } from '@/api/hooks';
import { cn } from '@/utils/cn';
import { useTranslation } from '@/i18n/useTranslation';

type TreasuryTab = 'cash' | 'debt';

const CURRENCY_FLAGS: Record<string, string> = {
  USD: '\uD83C\uDDFA\uD83C\uDDF8',
  EUR: '\uD83C\uDDEA\uD83C\uDDFA',
  GBP: '\uD83C\uDDEC\uD83C\uDDE7',
  CHF: '\uD83C\uDDE8\uD83C\uDDED',
  JPY: '\uD83C\uDDEF\uD83C\uDDF5',
  CNY: '\uD83C\uDDE8\uD83C\uDDF3',
  CAD: '\uD83C\uDDE8\uD83C\uDDE6',
  AUD: '\uD83C\uDDE6\uD83C\uDDFA',
  SEK: '\uD83C\uDDF8\uD83C\uDDEA',
  NOK: '\uD83C\uDDF3\uD83C\uDDF4',
  DKK: '\uD83C\uDDE9\uD83C\uDDF0',
  PLN: '\uD83C\uDDF5\uD83C\uDDF1',
  CZK: '\uD83C\uDDE8\uD83C\uDDFF',
  HUF: '\uD83C\uDDED\uD83C\uDDFA',
  RON: '\uD83C\uDDF7\uD83C\uDDF4',
  BGN: '\uD83C\uDDE7\uD83C\uDDEC',
  HRK: '\uD83C\uDDED\uD83C\uDDF7',
  TRY: '\uD83C\uDDF9\uD83C\uDDF7',
  MAD: '\uD83C\uDDF2\uD83C\uDDE6',
  ZAR: '\uD83C\uDDFF\uD83C\uDDE6',
  BRL: '\uD83C\uDDE7\uD83C\uDDF7',
  MXN: '\uD83C\uDDF2\uD83C\uDDFD',
  SGD: '\uD83C\uDDF8\uD83C\uDDEC',
  HKD: '\uD83C\uDDED\uD83C\uDDF0',
  INR: '\uD83C\uDDEE\uD83C\uDDF3',
  KRW: '\uD83C\uDDF0\uD83C\uDDF7',
};

const MATURITY_BANDS = [
  { key: '0_1y', label: '0-1Y', bg: 'bg-red-500' },
  { key: '1_3y', label: '1-3Y', bg: 'bg-amber-500' },
  { key: '3_5y', label: '3-5Y', bg: 'bg-blue-500' },
  { key: '5y_plus', label: '5Y+', bg: 'bg-emerald-500' },
];

function formatAmount(val: number): string {
  return new Intl.NumberFormat('en', { style: 'decimal', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
}

function formatCompact(val: number): string {
  if (Math.abs(val) >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`;
  if (Math.abs(val) >= 1_000) return `${(val / 1_000).toFixed(0)}K`;
  return formatAmount(val);
}

function maskAccount(acc: string): string {
  if (!acc || acc.length < 6) return acc || '-';
  return '\u2022\u2022\u2022\u2022 ' + acc.slice(-4);
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="card p-8">
        <div className="h-4 w-24 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
        <div className="mt-4 h-10 w-56 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
      </div>
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="card p-6">
            <div className="h-3 w-20 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
            <div className="mt-4 h-7 w-32 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
          </div>
        ))}
      </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="card p-16 text-center">
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-800">
        <svg className="h-8 w-8 text-slate-400 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{message}</p>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Cash Position Tab
// ────────────────────────────────────────────────────────────────────────────

function CashPositionTab({ siteId, date }: { siteId: string | null; date: string }) {
  const { t } = useTranslation();
  const { data: cashData, isLoading: cashLoading } = useCashPosition(siteId, date);
  const { data: accountsData, isLoading: accLoading } = useBankAccounts(siteId || '');

  if (cashLoading || accLoading) return <LoadingSkeleton />;

  const accounts = accountsData?.items ?? [];
  const position = cashData ?? {};
  const totalCash = position.total_cash ?? 0;

  return (
    <div className="space-y-6">
      {/* Cash position - simple card with large number */}
      <div className="card p-8">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t('treasury.totalCash')}</p>
        <p className="mt-2 text-4xl font-semibold font-mono tabular-nums text-slate-900 dark:text-white">
          {formatAmount(totalCash)}
        </p>

        <div className="mt-6 grid grid-cols-3 gap-4">
          {[
            { label: t('treasury.totalDeposits'), value: position.total_deposits ?? 0 },
            { label: t('treasury.totalCredit'), value: position.total_credit_lines ?? 0 },
            { label: t('treasury.netPosition'), value: position.net_position ?? 0 },
          ].map((m, i) => (
            <div key={i}>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{m.label}</p>
              <p className="mt-1 text-lg font-semibold font-mono tabular-nums text-slate-700 dark:text-slate-300">{formatCompact(m.value)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Bank Accounts */}
      {accounts.length === 0 ? (
        <EmptyState message={t('common.noData')} />
      ) : (
        <>
          <div className="flex items-center gap-3">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white">{t('treasury.bankAccounts')}</h2>
            <span className="pill-slate">{accounts.length}</span>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {accounts.map((acc: any, idx: number) => {
              const currency = acc.currency || 'EUR';
              const flag = CURRENCY_FLAGS[currency] || '';
              const status = (acc.status || 'active').toLowerCase();
              const isActive = status === 'active';

              return (
                <div key={acc.id || idx} className="card p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      {flag && <span className="text-lg">{flag}</span>}
                      <div>
                        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">{acc.bank_name || acc.bank}</h3>
                        <p className="text-xs font-mono tracking-wider text-slate-400 dark:text-slate-500">{maskAccount(acc.account_number || acc.iban)}</p>
                      </div>
                    </div>
                    <span className={cn(
                      'inline-flex items-center gap-1',
                      isActive ? 'pill-green' : 'pill-slate'
                    )}>
                      <span className={cn('h-1.5 w-1.5 rounded-full', isActive ? 'bg-emerald-500' : 'bg-slate-400')} />
                      {status}
                    </span>
                  </div>

                  <div className="mt-4 flex items-end justify-between">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t('treasury.balance')}</p>
                      <p className="mt-1 text-xl font-semibold font-mono tabular-nums text-slate-900 dark:text-white">
                        {formatAmount(acc.balance ?? 0)}
                      </p>
                    </div>
                    <span className="pill-slate">{currency}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Debt Profile Tab
// ────────────────────────────────────────────────────────────────────────────

function MaturityTimeline({ profile }: { profile: any }) {
  const buckets = MATURITY_BANDS.map((band) => ({
    ...band,
    value: profile[band.key] ?? 0,
  }));
  const total = buckets.reduce((s, b) => s + b.value, 0);
  if (total <= 0) return null;

  return (
    <div className="card p-6">
      <h3 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-5">Maturity Timeline</h3>

      {/* Stacked bar */}
      <div className="flex h-6 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
        {buckets.map((b) => {
          const pct = (b.value / total) * 100;
          if (pct < 0.5) return null;
          return (
            <div
              key={b.key}
              className={cn('h-full transition-all duration-700', b.bg)}
              style={{ width: `${pct}%` }}
              title={`${b.label}: ${formatAmount(b.value)}`}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {buckets.map((b) => (
          <div key={b.key} className="flex items-center gap-3">
            <div className={cn('h-3 w-3 rounded-full', b.bg)} />
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{b.label}</p>
              <p className="text-sm font-semibold font-mono tabular-nums text-slate-800 dark:text-slate-200">{formatCompact(b.value)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DebtProfileTab() {
  const { t } = useTranslation();
  const { data, isLoading } = useDebtMaturity();

  if (isLoading) return <LoadingSkeleton />;

  const instruments = data?.instruments ?? data?.items ?? [];
  const profile = data?.maturity_profile ?? data?.profile ?? {};

  const summaryDefs = [
    { label: t('treasury.totalDebt'), value: profile.total_debt ?? 0 },
    { label: t('treasury.shortTerm'), value: profile.short_term ?? 0 },
    { label: t('treasury.longTerm'), value: profile.long_term ?? 0 },
    { label: t('treasury.avgRate'), value: profile.weighted_avg_rate != null ? `${profile.weighted_avg_rate.toFixed(2)}%` : '-', raw: true },
  ];

  const BORDER_COLORS = ['border-l-red-500', 'border-l-amber-500', 'border-l-blue-500', 'border-l-violet-500'];

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      {Object.keys(profile).length > 0 && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {summaryDefs.map((card, i) => (
            <div key={i} className={cn('card border-l-4 p-5', BORDER_COLORS[i])}>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{card.label}</p>
              <p className="mt-2 text-2xl font-semibold font-mono tabular-nums text-slate-900 dark:text-white">
                {card.raw ? card.value : formatAmount(card.value as number)}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Maturity timeline */}
      <MaturityTimeline profile={profile} />

      {/* Debt instruments table */}
      {instruments.length === 0 ? (
        <EmptyState message={t('common.noData')} />
      ) : (
        <div className="card overflow-hidden">
          <div className="flex items-center gap-3 border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white">{t('treasury.debtInstruments')}</h2>
            <span className="pill-slate">{instruments.length}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-700/50">
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Lender</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Rate</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">{t('treasury.principal')}</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">{t('treasury.outstanding')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Maturity</th>
                </tr>
              </thead>
              <tbody>
                {instruments.map((d: any, idx: number) => (
                  <tr key={d.id || idx} className="border-b border-slate-50 transition-colors hover:bg-slate-50 dark:border-slate-800/50 dark:hover:bg-slate-700/20">
                    <td className="px-6 py-3"><span className="pill-violet">{d.instrument_type || d.type || '-'}</span></td>
                    <td className="px-6 py-3 text-sm font-medium text-slate-800 dark:text-slate-200">{d.lender || d.bank || '-'}</td>
                    <td className="px-6 py-3 text-sm text-right font-mono tabular-nums text-slate-600 dark:text-slate-400">{d.interest_rate != null ? `${d.interest_rate}%` : '-'}</td>
                    <td className="px-6 py-3 text-sm text-right font-mono tabular-nums text-slate-600 dark:text-slate-400">{formatAmount(d.principal ?? d.original_amount ?? 0)}</td>
                    <td className="px-6 py-3 text-sm text-right font-mono tabular-nums font-semibold text-slate-800 dark:text-slate-200">{formatAmount(d.outstanding ?? d.balance ?? 0)}</td>
                    <td className="px-6 py-3 text-sm text-slate-500 dark:text-slate-400">{d.maturity_date || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Main Page
// ────────────────────────────────────────────────────────────────────────────

export function TreasuryPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<TreasuryTab>('cash');
  const selectedSiteId = useDashboardStore((s) => s.selectedSiteId);
  const selectedYear = useDashboardStore((s) => s.selectedYear);
  const selectedMonth = useDashboardStore((s) => s.selectedMonth);
  const { data: sites } = useSites();

  const siteName = useMemo(() => {
    if (!selectedSiteId || !sites) return t('common.consolidated');
    return sites.find((s) => s.id === selectedSiteId)?.name ?? 'Unknown Site';
  }, [selectedSiteId, sites, t]);

  const dateStr = `${selectedYear}-${String(selectedMonth).padStart(2, '0')}-01`;

  return (
    <div className="page-enter space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
          {t('treasury.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{siteName}</p>
      </div>

      {/* Underline tabs */}
      <div className="flex gap-6 border-b border-slate-200 mb-6">
        {[
          { key: 'cash' as TreasuryTab, labelKey: 'treasury.cashTab' },
          { key: 'debt' as TreasuryTab, labelKey: 'treasury.debtTab' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn('pb-3 text-sm font-medium border-b-2 -mb-px transition-colors',
              activeTab === tab.key ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700'
            )}
          >
            {t(tab.labelKey)}
          </button>
        ))}
      </div>

      {activeTab === 'cash' && <CashPositionTab siteId={selectedSiteId} date={dateStr} />}
      {activeTab === 'debt' && <DebtProfileTab />}
    </div>
  );
}
