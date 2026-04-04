import React, { useState } from 'react';
import { cn } from '@/utils/cn';

interface WidgetWrapperProps {
  title: string;
  periodLabel?: string;
  children: React.ReactNode;
  onExpand?: () => void;
  onSettings?: () => void;
  className?: string;
}

export function WidgetWrapper({
  title,
  periodLabel,
  children,
  onExpand,
  onSettings,
  className,
}: WidgetWrapperProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={cn(
        'flex h-full flex-col card',
        'hover:shadow-card-hover',
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Title Bar */}
      <div className="flex items-center justify-between border-b border-slate-200/30 px-5 py-3.5 dark:border-slate-600/20 widget-drag-handle cursor-grab active:cursor-grabbing">
        <div className="flex items-center gap-2.5">
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            {title}
          </h3>
          {periodLabel && (
            <span className="rounded-lg bg-slate-100/80 px-2 py-0.5 text-[10px] font-medium text-slate-500 dark:bg-slate-700/50 dark:text-slate-400">
              {periodLabel}
            </span>
          )}
        </div>
        <div
          className={cn(
            'flex items-center gap-1 transition-opacity duration-200',
            isHovered ? 'opacity-100' : 'opacity-0'
          )}
        >
          {onExpand && (
            <button
              onClick={onExpand}
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100/60 hover:text-slate-600 dark:hover:bg-slate-700/50 transition-all duration-150"
              aria-label="Expand widget"
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
          )}
          {onSettings && (
            <button
              onClick={onSettings}
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100/60 hover:text-slate-600 dark:hover:bg-slate-700/50 transition-all duration-150"
              aria-label="Widget settings"
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden p-5">
        {children}
      </div>
    </div>
  );
}
