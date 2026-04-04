import { cn } from '@/utils/cn';
import { useTranslation } from '@/i18n/useTranslation';
import type { KPICardData } from '@/types/kpi';

const BORDER_COLORS: Record<string, string> = {
  blue: 'border-l-blue-500',
  emerald: 'border-l-emerald-500',
  violet: 'border-l-violet-500',
  pink: 'border-l-pink-500',
  cyan: 'border-l-cyan-500',
  amber: 'border-l-amber-500',
};

export function KPICard({ data }: { data: KPICardData }) {
  const { t } = useTranslation();

  return (
    <div className={cn('card p-5 border-l-4', BORDER_COLORS[data.color || 'blue'] || BORDER_COLORS.blue)}>
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{data.label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{data.formattedValue}</p>
      {data.benchmark !== undefined && (
        <p className="mt-2 text-xs text-slate-400">
          {t('kpi.benchmark')}: {data.benchmark.toFixed(1)}
        </p>
      )}
    </div>
  );
}
