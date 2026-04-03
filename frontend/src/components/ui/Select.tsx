import React from 'react';
import { cn } from '@/utils/cn';

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  options: SelectOption[];
  placeholder?: string;
  label?: string;
  error?: string;
}

export function Select({
  className,
  options,
  placeholder,
  label,
  error,
  id,
  ...props
}: SelectProps) {
  const selectId = id || label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={selectId} className="label">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={cn(
          'input-base appearance-none bg-no-repeat pr-10',
          'bg-[url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%2712%27 height=%2712%27 viewBox=%270 0 12 12%27%3E%3Cpath fill=%27%236b7280%27 d=%27M2.22 4.47a.75.75 0 0 1 1.06 0L6 7.19l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L2.22 5.53a.75.75 0 0 1 0-1.06z%27/%3E%3C/svg%3E")]',
          'bg-[position:right_0.75rem_center]',
          error && 'border-negative-500 focus:border-negative-500 focus:ring-negative-500/20',
          className
        )}
        {...props}
      >
        {placeholder && (
          <option value="">
            {placeholder}
          </option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} disabled={opt.disabled}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-xs text-negative-600">{error}</p>
      )}
    </div>
  );
}
