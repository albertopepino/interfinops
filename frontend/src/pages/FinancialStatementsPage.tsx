import { useState, useMemo } from 'react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useSites, useSiteStatements, useConsolidatedFinancialData } from '@/api/hooks';
import { formatCurrency, formatPeriod, formatDateTime } from '@/utils/formatters';
import { cn } from '@/utils/cn';
import { useTranslation } from '@/i18n/useTranslation';

type StatementTab = 'income_statement' | 'balance_sheet' | 'cash_flow';

const TAB_DEFS: { key: StatementTab; translationKey: string; icon: string }[] = [
  { key: 'income_statement', translationKey: 'statements.incomeStatement', icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' },
  { key: 'balance_sheet', translationKey: 'statements.balanceSheet', icon: 'M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3' },
  { key: 'cash_flow', translationKey: 'statements.cashFlow', icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z' },
];

// Code-to-name mapping and hierarchy definition
const LINE_ITEM_META: Record<string, { name: string; parent: string | null; isSummary?: boolean }> = {
  // Income Statement
  REV: { name: 'Revenue / Net Sales', parent: null },
  REV_GOODS: { name: 'Sales of Goods', parent: 'REV' },
  REV_SERVICES: { name: 'Sales of Services', parent: 'REV' },
  REV_OTHER: { name: 'Other Revenue', parent: 'REV' },
  COGS: { name: 'Cost of Goods Sold', parent: null },
  COGS_RAW: { name: 'Raw Materials', parent: 'COGS' },
  COGS_LABOR: { name: 'Direct Labor', parent: 'COGS' },
  COGS_OH: { name: 'Manufacturing Overhead', parent: 'COGS' },
  GP: { name: 'Gross Profit', parent: null, isSummary: true },
  OPEX: { name: 'Operating Expenses', parent: null },
  OPEX_SAL: { name: 'Salaries & Wages', parent: 'OPEX' },
  OPEX_RENT: { name: 'Rent & Utilities', parent: 'OPEX' },
  OPEX_DA: { name: 'Depreciation & Amortization', parent: 'OPEX' },
  OPEX_MKT: { name: 'Marketing & Advertising', parent: 'OPEX' },
  OPEX_PROF: { name: 'Professional Fees', parent: 'OPEX' },
  OPEX_TRAVEL: { name: 'Travel & Entertainment', parent: 'OPEX' },
  OPEX_INS: { name: 'Insurance', parent: 'OPEX' },
  OPEX_OTHER: { name: 'Other Operating Expenses', parent: 'OPEX' },
  EBIT: { name: 'Operating Income (EBIT)', parent: null, isSummary: true },
  OTH_INC: { name: 'Interest Income', parent: null },
  OTH_EXP: { name: 'Interest Expense', parent: null },
  OTH_FX: { name: 'FX Gains / Losses', parent: null },
  IC_INC: { name: 'Intercompany Income', parent: null },
  IC_EXP: { name: 'Intercompany Expenses', parent: null },
  EBT: { name: 'Earnings Before Tax', parent: null, isSummary: true },
  TAX: { name: 'Income Tax', parent: null },
  NI: { name: 'Net Income', parent: null, isSummary: true },
  // Balance Sheet
  CA: { name: 'Current Assets', parent: null },
  CA_CASH: { name: 'Cash & Bank Balances', parent: 'CA' },
  CA_AR: { name: 'Accounts Receivable', parent: 'CA' },
  CA_IC_AR: { name: 'Intercompany Receivables', parent: 'CA' },
  CA_INV: { name: 'Inventory', parent: 'CA' },
  CA_PREPAID: { name: 'Prepaid Expenses', parent: 'CA' },
  CA_OTHER: { name: 'Other Current Assets', parent: 'CA' },
  NCA: { name: 'Non-Current Assets', parent: null },
  NCA_PPE: { name: 'Property, Plant & Equipment', parent: 'NCA' },
  NCA_INTANG: { name: 'Intangible Assets', parent: 'NCA' },
  NCA_INVEST: { name: 'Long-term Investments', parent: 'NCA' },
  NCA_DEP: { name: 'Deposits & Advances', parent: 'NCA' },
  NCA_OTHER: { name: 'Other Non-Current Assets', parent: 'NCA' },
  TA: { name: 'Total Assets', parent: null, isSummary: true },
  CL: { name: 'Current Liabilities', parent: null },
  CL_AP: { name: 'Accounts Payable', parent: 'CL' },
  CL_IC_AP: { name: 'Intercompany Payables', parent: 'CL' },
  CL_STD: { name: 'Short-term Debt', parent: 'CL' },
  CL_ACCR: { name: 'Accrued Expenses', parent: 'CL' },
  CL_WAGES: { name: 'Wages Payable', parent: 'CL' },
  CL_TAX: { name: 'Taxes Payable', parent: 'CL' },
  CL_OTHER: { name: 'Other Current Liabilities', parent: 'CL' },
  NCL: { name: 'Non-Current Liabilities', parent: null },
  NCL_LTD: { name: 'Long-term Debt', parent: 'NCL' },
  NCL_PROV: { name: 'Provisions & Accruals', parent: 'NCL' },
  NCL_OTHER: { name: 'Other Non-Current Liabilities', parent: 'NCL' },
  TL: { name: 'Total Liabilities', parent: null, isSummary: true },
  EQ: { name: 'Total Equity', parent: null },
  EQ_SC: { name: 'Share Capital', parent: 'EQ' },
  EQ_RE: { name: 'Retained Earnings', parent: 'EQ' },
  EQ_RES: { name: 'Other Reserves', parent: 'EQ' },
  EQ_FX: { name: 'FX Translation Reserve', parent: 'EQ' },
  TLE: { name: 'Total Liabilities + Equity', parent: null, isSummary: true },
  // Cash Flow
  CFO: { name: 'Net Cash from Operations', parent: null, isSummary: true },
  CFO_NI: { name: 'Net Income', parent: 'CFO' },
  CFO_DA: { name: 'Depreciation & Amortization', parent: 'CFO' },
  CFO_AR: { name: 'Change in Accounts Receivable', parent: 'CFO' },
  CFO_INV: { name: 'Change in Inventory', parent: 'CFO' },
  CFO_AP: { name: 'Change in Accounts Payable', parent: 'CFO' },
  CFO_OTHER: { name: 'Change in Other Current Items', parent: 'CFO' },
  CFI: { name: 'Net Cash from Investing', parent: null, isSummary: true },
  CFI_CAPEX: { name: 'Capital Expenditures', parent: 'CFI' },
  CFI_INVEST: { name: 'Acquisition of Investments', parent: 'CFI' },
  CFI_SALE: { name: 'Proceeds from Asset Sales', parent: 'CFI' },
  CFF: { name: 'Net Cash from Financing', parent: null, isSummary: true },
  CFF_DEBT_IN: { name: 'Proceeds from Debt', parent: 'CFF' },
  CFF_DEBT_OUT: { name: 'Repayment of Debt', parent: 'CFF' },
  CFF_DIV: { name: 'Dividends Paid', parent: 'CFF' },
  CFF_IC: { name: 'Intercompany Loans (Net)', parent: 'CFF' },
  NET_CASH: { name: 'Net Change in Cash', parent: null, isSummary: true },
  OPEN_CASH: { name: 'Opening Cash Balance', parent: null },
  CLOSE_CASH: { name: 'Closing Cash Balance', parent: null, isSummary: true },
};

interface DisplayRow {
  code: string;
  name: string;
  amount: number;
  isHeader: boolean;
  isSummary: boolean;
  isChild: boolean;
}

function buildDisplayRows(data: Record<string, number | string>): DisplayRow[] {
  const amounts = new Map<string, number>();
  for (const [code, val] of Object.entries(data)) {
    amounts.set(code, typeof val === 'string' ? parseFloat(val) || 0 : val);
  }

  const rows: DisplayRow[] = [];
  const parentCodes = new Set<string>();

  // First find which codes are parents
  for (const code of amounts.keys()) {
    const meta = LINE_ITEM_META[code];
    if (meta?.parent) parentCodes.add(meta.parent);
  }

  // Build ordered rows with hierarchy
  const processed = new Set<string>();

  for (const code of amounts.keys()) {
    if (processed.has(code)) continue;
    const meta = LINE_ITEM_META[code];
    if (!meta) {
      rows.push({ code, name: code, amount: amounts.get(code) || 0, isHeader: false, isSummary: false, isChild: false });
      processed.add(code);
      continue;
    }
    if (meta.parent) continue; // Will be rendered under parent

    // This is a top-level item
    const isParent = parentCodes.has(code);
    rows.push({
      code, name: meta.name, amount: amounts.get(code) || 0,
      isHeader: isParent, isSummary: !!meta.isSummary, isChild: false,
    });
    processed.add(code);

    // Add children
    if (isParent) {
      for (const [childCode, childVal] of amounts.entries()) {
        const childMeta = LINE_ITEM_META[childCode];
        if (childMeta?.parent === code && !processed.has(childCode)) {
          rows.push({
            code: childCode, name: childMeta.name,
            amount: typeof childVal === 'string' ? parseFloat(childVal as string) || 0 : childVal as number,
            isHeader: false, isSummary: false, isChild: true,
          });
          processed.add(childCode);
        }
      }
    }
  }

  return rows;
}

function formatAmt(amount: number, currency: string): string {
  if (amount < 0) return `(${formatCurrency(Math.abs(amount), currency)})`;
  return formatCurrency(amount, currency);
}

// ─── Components ────────────────────────────────────────────────────────────

function StatementTable({ rows, currency }: { rows: DisplayRow[]; currency: string }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200/60 dark:border-slate-700/40">
            <th className="px-6 py-3.5 text-left text-[11px] font-semibold uppercase tracking-widest text-slate-400">
              Account
            </th>
            <th className="px-6 py-3.5 text-right text-[11px] font-semibold uppercase tracking-widest text-slate-400 w-52">
              Amount ({currency})
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.code}
              className={cn(
                'border-b transition-colors duration-150',
                row.isSummary
                  ? 'border-slate-200/80 bg-slate-50/80 dark:bg-slate-800/50 dark:border-slate-700/40'
                  : row.isHeader
                  ? 'border-slate-100/60 bg-slate-50/40 dark:bg-slate-800/30 dark:border-slate-700/30'
                  : 'border-slate-100/40 hover:bg-blue-50/30 dark:border-slate-700/20 dark:hover:bg-slate-700/20',
              )}
            >
              <td className={cn(
                'py-3 text-sm',
                row.isChild ? 'pl-12 pr-6' : 'px-6',
                row.isSummary ? 'font-bold text-slate-900 dark:text-white' : '',
                row.isHeader && !row.isSummary ? 'font-semibold text-slate-800 dark:text-slate-200' : '',
                !row.isHeader && !row.isSummary ? 'text-slate-600 dark:text-slate-400' : '',
              )}>
                {row.isSummary && (
                  <span className="mr-2 text-slate-400">=</span>
                )}
                {row.name}
              </td>
              <td className={cn(
                'px-6 py-3 text-right font-mono text-sm tabular-nums',
                row.isSummary ? 'font-bold' : '',
                row.amount < 0 ? 'text-red-500 dark:text-red-400' :
                  row.isSummary ? 'text-slate-900 dark:text-white' : 'text-slate-700 dark:text-slate-300',
                row.isSummary && 'border-t-2 border-slate-300 dark:border-slate-600',
              )}>
                {formatAmt(row.amount, currency)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SiteStatementView({ siteId, year, month, statementType, siteName }: {
  siteId: string; year: number; month: number; statementType: StatementTab; siteName: string;
}) {
  const { data, isLoading, isError } = useSiteStatements(siteId, year, month, statementType);

  if (isLoading) return <LoadingSkeleton />;
  if (isError) return <ErrorState />;

  const items = data?.items ?? [];
  if (items.length === 0) return <EmptyState />;

  const stmt = items[0] as any;
  const lineItemMap: Record<string, number> = {};
  for (const li of stmt.line_items) {
    lineItemMap[li.line_item_code] = li.amount;
  }
  const rows = buildDisplayRows(lineItemMap);

  return (
    <div className="glass-card overflow-hidden animate-in">
      <div className="border-b border-white/10 px-6 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">{siteName}</h2>
            <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
              {formatPeriod(year, month)} &middot; {stmt.currency}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={stmt.status} />
            <span className="text-xs text-slate-400">
              {formatDateTime(stmt.uploaded_at)}
            </span>
          </div>
        </div>
      </div>
      <StatementTable rows={rows} currency={stmt.currency} />
    </div>
  );
}

function ConsolidatedStatementView({ year, month, statementType }: {
  year: number; month: number; statementType: StatementTab;
}) {
  const { data, isLoading, isError } = useConsolidatedFinancialData(year, month);

  if (isLoading) return <LoadingSkeleton />;
  if (isError) return <ErrorState />;

  const statementData = data?.[statementType];
  if (!statementData || Object.keys(statementData).length === 0) return <EmptyState />;

  const rows = buildDisplayRows(statementData);

  return (
    <div className="glass-card overflow-hidden animate-in">
      <div className="border-b border-white/10 px-6 py-5">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Consolidated</h2>
        <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
          {formatPeriod(year, month)} &middot; EUR
        </p>
      </div>
      <StatementTable rows={rows} currency="EUR" />
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    approved: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    submitted: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    draft: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
  };
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold', styles[status] || styles.draft)}>
      <span className={cn('h-1.5 w-1.5 rounded-full', status === 'approved' ? 'bg-emerald-500' : status === 'submitted' ? 'bg-blue-500' : 'bg-slate-400')} />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

function LoadingSkeleton() {
  return (
    <div className="glass-card overflow-hidden">
      <div className="border-b border-white/10 px-6 py-5">
        <div className="h-5 w-48 animate-pulse rounded-lg bg-slate-200/60 dark:bg-slate-700/60" />
        <div className="mt-2 h-4 w-32 animate-pulse rounded-lg bg-slate-100/60 dark:bg-slate-700/40" />
      </div>
      <div className="p-6 space-y-3">
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} className="flex justify-between">
            <div className="h-4 animate-pulse rounded bg-slate-100/60 dark:bg-slate-700/40" style={{ width: `${120 + Math.random() * 150}px` }} />
            <div className="h-4 w-24 animate-pulse rounded bg-slate-100/60 dark:bg-slate-700/40" />
          </div>
        ))}
      </div>
    </div>
  );
}

function ErrorState() {
  return (
    <div className="glass-card p-10 text-center">
      <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10">
        <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <p className="text-sm text-red-600 dark:text-red-400">Failed to load data. Please try again.</p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="glass-card p-12 text-center">
      <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-500/10">
        <svg className="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <p className="text-sm text-slate-500 dark:text-slate-400">No statement data available for this period.</p>
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────

export function FinancialStatementsPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<StatementTab>('income_statement');
  const selectedSiteId = useDashboardStore((s) => s.selectedSiteId);
  const selectedYear = useDashboardStore((s) => s.selectedYear);
  const selectedMonth = useDashboardStore((s) => s.selectedMonth);
  const { data: sites } = useSites();

  const siteName = useMemo(() => {
    if (!selectedSiteId || !sites) return t('common.allSites');
    return sites.find((s) => s.id === selectedSiteId)?.name ?? 'Unknown Site';
  }, [selectedSiteId, sites]);

  return (
    <div className="space-y-6 animate-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          {t('statements.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {siteName} &middot; {formatPeriod(selectedYear, selectedMonth)}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {TAB_DEFS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              'inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-200',
              activeTab === tab.key
                ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25'
                : 'glass-card !rounded-xl text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
            )}
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={tab.icon} />
            </svg>
            {t(tab.translationKey)}
          </button>
        ))}
      </div>

      {/* Content */}
      {selectedSiteId ? (
        <SiteStatementView siteId={selectedSiteId} year={selectedYear} month={selectedMonth} statementType={activeTab} siteName={siteName} />
      ) : (
        <ConsolidatedStatementView year={selectedYear} month={selectedMonth} statementType={activeTab} />
      )}
    </div>
  );
}
