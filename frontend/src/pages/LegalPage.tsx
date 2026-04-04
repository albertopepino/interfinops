import { useState } from 'react';
import { useLegalEntities, useStatutoryAudits } from '@/api/hooks';
import { cn } from '@/utils/cn';
import { useTranslation } from '@/i18n/useTranslation';
import { useDashboardStore } from '@/store/dashboardStore';

type LegalTab = 'entities' | 'directors' | 'audits';

const ENTITY_TYPE_PILLS: Record<string, string> = {
  holding: 'pill-violet',
  operating: 'pill-blue',
  dormant: 'pill-slate',
  spv: 'pill-amber',
  branch: 'pill-blue',
};

const AUDIT_STATUS_PILLS: Record<string, string> = {
  not_started: 'pill-slate',
  in_progress: 'pill-blue',
  draft_report: 'pill-amber',
  final_report: 'pill-green',
  filed: 'pill-green',
  completed: 'pill-green',
  scheduled: 'pill-amber',
  overdue: 'pill-red',
  pending: 'pill-slate',
};

const AUDIT_DOT_COLORS: Record<string, string> = {
  not_started: 'bg-slate-400',
  in_progress: 'bg-blue-500',
  draft_report: 'bg-amber-500',
  final_report: 'bg-emerald-500',
  filed: 'bg-emerald-500',
  completed: 'bg-emerald-500',
  scheduled: 'bg-amber-500',
  overdue: 'bg-red-500',
  pending: 'bg-slate-400',
};

function StatusBadge({ status }: { status: string }) {
  const s = status.toLowerCase().replace(/[\s]+/g, '_');
  const pill = AUDIT_STATUS_PILLS[s] || 'pill-slate';
  const dot = AUDIT_DOT_COLORS[s] || 'bg-slate-400';
  return (
    <span className={cn(pill, 'inline-flex items-center gap-1.5')}>
      <span className={cn('h-1.5 w-1.5 rounded-full', dot)} />
      {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
    </span>
  );
}

function TypeBadge({ type }: { type: string }) {
  const key = type.toLowerCase().replace(/[\s]+/g, '_');
  const pill = ENTITY_TYPE_PILLS[key] || 'pill-slate';
  return <span className={pill}>{type}</span>;
}

function LoadingSkeleton() {
  return (
    <div className="card overflow-hidden">
      <div className="p-6 space-y-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex justify-between">
            <div className="h-4 animate-pulse rounded bg-slate-100 dark:bg-slate-700" style={{ width: `${120 + Math.random() * 150}px` }} />
            <div className="h-4 w-24 animate-pulse rounded bg-slate-100 dark:bg-slate-700" />
          </div>
        ))}
      </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="card p-12 text-center">
      <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <svg className="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      </div>
      <p className="text-sm text-slate-500 dark:text-slate-400">{message}</p>
    </div>
  );
}

function EntitiesTab() {
  const { t } = useTranslation();
  const { data, isLoading } = useLegalEntities();

  if (isLoading) return <LoadingSkeleton />;
  const items = data?.items ?? [];
  if (items.length === 0) return <EmptyState message={t('common.noData')} />;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((e: any, idx: number) => (
        <div key={e.id || idx} className="card p-5">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">{e.name || e.entity_name}</h3>
              <p className="mt-0.5 text-xs font-mono text-slate-400 dark:text-slate-500">{e.registration_number || e.reg_number || '-'}</p>
            </div>
            <TypeBadge type={e.entity_type || e.type || '-'} />
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.jurisdiction')}</p>
              <p className="mt-0.5 text-sm text-slate-700 dark:text-slate-300">{e.jurisdiction || e.country || '-'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.ownership')}</p>
              <p className="mt-0.5 text-sm font-mono tabular-nums text-slate-700 dark:text-slate-300">{e.ownership_pct != null ? `${e.ownership_pct}%` : '-'}</p>
            </div>
          </div>

          <div className="mt-4">
            <StatusBadge status={e.status || 'active'} />
          </div>
        </div>
      ))}
    </div>
  );
}

function DirectorsTab() {
  const { t } = useTranslation();
  const { data, isLoading } = useLegalEntities();

  if (isLoading) return <LoadingSkeleton />;
  const entities = data?.items ?? [];
  if (entities.length === 0) return <EmptyState message={t('common.noData')} />;

  const entitiesWithDirectors = entities.filter((e: any) => e.directors && e.directors.length > 0);
  if (entitiesWithDirectors.length === 0) return <EmptyState message={t('common.noData')} />;

  return (
    <div className="space-y-4">
      {entitiesWithDirectors.map((entity: any, idx: number) => (
        <div key={entity.id || idx} className="card overflow-hidden">
          <div className="border-b border-slate-200 px-6 py-4 flex items-center justify-between dark:border-slate-700">
            <div>
              <h3 className="text-base font-semibold text-slate-900 dark:text-white">{entity.name || entity.entity_name}</h3>
              <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{entity.jurisdiction || entity.country}</p>
            </div>
            <span className="pill-slate">{entity.directors.length}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-700/50">
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.directorName')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.role')}</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.appointedDate')}</th>
                </tr>
              </thead>
              <tbody>
                {entity.directors.map((d: any, dIdx: number) => (
                  <tr key={dIdx} className="border-b border-slate-50 transition-colors hover:bg-slate-50 dark:border-slate-700/20 dark:hover:bg-slate-700/20">
                    <td className="px-6 py-3 text-sm font-medium text-slate-700 dark:text-slate-300">{d.name || d.full_name}</td>
                    <td className="px-6 py-3"><span className="pill-blue">{d.role || d.position || '-'}</span></td>
                    <td className="px-6 py-3 text-sm text-slate-500 dark:text-slate-400">{d.appointed_date || d.start_date || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}

function AuditsTab() {
  const { t } = useTranslation();
  const selectedYear = useDashboardStore((s) => s.selectedYear);
  const { data, isLoading } = useStatutoryAudits(selectedYear);

  if (isLoading) return <LoadingSkeleton />;
  const items = data?.items ?? [];
  if (items.length === 0) return <EmptyState message={t('common.noData')} />;

  return (
    <div className="card overflow-hidden">
      <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
        <h2 className="text-base font-semibold text-slate-900 dark:text-white">{t('legal.audits')}</h2>
        <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{selectedYear}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100 dark:border-slate-700/50">
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.entityName')}</th>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.auditor')}</th>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('legal.auditType')}</th>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('tax.dueDate')}</th>
              <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">{t('common.status')}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((a: any, idx: number) => (
              <tr key={a.id || idx} className="border-b border-slate-50 transition-colors hover:bg-slate-50 dark:border-slate-700/20 dark:hover:bg-slate-700/20">
                <td className="px-6 py-3 text-sm font-medium text-slate-700 dark:text-slate-300">{a.entity_name || a.name}</td>
                <td className="px-6 py-3 text-sm text-slate-500 dark:text-slate-400">{a.auditor || a.audit_firm || '-'}</td>
                <td className="px-6 py-3 text-sm text-slate-500 dark:text-slate-400">{a.audit_type || a.type || '-'}</td>
                <td className="px-6 py-3 text-sm text-slate-500 dark:text-slate-400">{a.due_date || a.deadline || '-'}</td>
                <td className="px-6 py-3"><StatusBadge status={a.status || 'pending'} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function LegalPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<LegalTab>('entities');

  const TAB_DEFS: { key: LegalTab; labelKey: string }[] = [
    { key: 'entities', labelKey: 'legal.entitiesTab' },
    { key: 'directors', labelKey: 'legal.directorsTab' },
    { key: 'audits', labelKey: 'legal.auditsTab' },
  ];

  return (
    <div className="page-enter space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
          {t('legal.title')}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {t('legal.subtitle')}
        </p>
      </div>

      <div className="flex gap-6 border-b border-slate-200 mb-6">
        {TAB_DEFS.map((tab) => (
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

      {activeTab === 'entities' && <EntitiesTab />}
      {activeTab === 'directors' && <DirectorsTab />}
      {activeTab === 'audits' && <AuditsTab />}
    </div>
  );
}
