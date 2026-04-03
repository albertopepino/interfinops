import React from 'react';
import { cn } from '@/utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

const variantClasses = {
  primary:
    'bg-gradient-to-b from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25 hover:from-blue-600 hover:to-blue-700 hover:shadow-blue-500/30 focus:ring-blue-500/30 disabled:from-blue-300 disabled:to-blue-400 disabled:shadow-none',
  secondary:
    'border border-slate-200/60 bg-white/80 backdrop-blur-sm text-slate-700 hover:bg-white hover:border-slate-300 hover:shadow-sm focus:ring-slate-500/20 dark:border-slate-600/40 dark:bg-slate-800/80 dark:text-slate-300 dark:hover:bg-slate-700/80',
  danger:
    'bg-gradient-to-b from-red-500 to-red-600 text-white shadow-lg shadow-red-500/25 hover:from-red-600 hover:to-red-700 hover:shadow-red-500/30 focus:ring-red-500/30 disabled:from-red-300 disabled:to-red-400 disabled:shadow-none',
  ghost:
    'bg-transparent text-slate-600 hover:bg-slate-100/80 dark:text-slate-400 dark:hover:bg-slate-700/50',
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-2.5 text-base',
};

export function Button({
  className,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  icon,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-xl font-semibold',
        'transition-all duration-200 active:scale-[0.98]',
        'focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:opacity-60',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <svg
          className="h-4 w-4 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  );
}
