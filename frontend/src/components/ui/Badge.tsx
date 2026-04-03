import { cn } from '@/utils/cn';

interface BadgeProps {
  variant?: 'positive' | 'negative' | 'neutral' | 'info' | 'warning';
  size?: 'sm' | 'md';
  children: React.ReactNode;
  className?: string;
}

const variantClasses = {
  positive: 'bg-positive-50 text-positive-700 dark:bg-positive-700/20 dark:text-positive-400',
  negative: 'bg-negative-50 text-negative-700 dark:bg-negative-700/20 dark:text-negative-400',
  neutral: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
  info: 'bg-blue-50 text-blue-700 dark:bg-blue-700/20 dark:text-blue-400',
  warning: 'bg-amber-50 text-amber-700 dark:bg-amber-700/20 dark:text-amber-400',
};

const sizeClasses = {
  sm: 'px-1.5 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
};

export function Badge({
  variant = 'neutral',
  size = 'md',
  className,
  children,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
}
