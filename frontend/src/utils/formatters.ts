const CURRENCY_LOCALES: Record<string, string> = {
  EUR: 'de-DE',
  USD: 'en-US',
  GBP: 'en-GB',
  CHF: 'de-CH',
  SEK: 'sv-SE',
  NOK: 'nb-NO',
  DKK: 'da-DK',
  PLN: 'pl-PL',
  CZK: 'cs-CZ',
  HUF: 'hu-HU',
  RON: 'ro-RO',
};

export function formatCurrency(
  amount: number,
  currency: string = 'EUR',
  options?: { compact?: boolean; decimals?: number }
): string {
  const locale = CURRENCY_LOCALES[currency] || 'en-US';
  const compact = options?.compact ?? false;
  const decimals = options?.decimals;

  if (compact) {
    return abbreviateNumber(amount, currency, locale);
  }

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals ?? 0,
    maximumFractionDigits: decimals ?? 2,
  }).format(amount);
}

export function abbreviateNumber(
  amount: number,
  currency?: string,
  locale?: string
): string {
  const absAmount = Math.abs(amount);
  const sign = amount < 0 ? '-' : '';
  const curr = currency || 'EUR';
  const loc = locale || CURRENCY_LOCALES[curr] || 'en-US';

  let abbreviated: string;
  if (absAmount >= 1_000_000_000) {
    abbreviated = (absAmount / 1_000_000_000).toFixed(1) + 'B';
  } else if (absAmount >= 1_000_000) {
    abbreviated = (absAmount / 1_000_000).toFixed(1) + 'M';
  } else if (absAmount >= 1_000) {
    abbreviated = (absAmount / 1_000).toFixed(1) + 'K';
  } else {
    abbreviated = absAmount.toFixed(0);
  }

  const symbol = new Intl.NumberFormat(loc, {
    style: 'currency',
    currency: curr,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })
    .formatToParts(0)
    .find((p) => p.type === 'currency')?.value || curr;

  return `${sign}${symbol}${abbreviated}`;
}

export function formatPercent(
  value: number,
  options?: { decimals?: number; showSign?: boolean }
): string {
  const decimals = options?.decimals ?? 1;
  const showSign = options?.showSign ?? false;
  const formatted = value.toFixed(decimals) + '%';
  if (showSign && value > 0) {
    return '+' + formatted;
  }
  return formatted;
}

export function formatNumber(
  value: number,
  options?: { decimals?: number; locale?: string }
): string {
  const decimals = options?.decimals ?? 2;
  const locale = options?.locale ?? 'en-US';
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: 0,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatRatio(value: number, decimals: number = 2): string {
  return value.toFixed(decimals) + 'x';
}

export function formatDays(value: number): string {
  return Math.round(value) + ' days';
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function formatPeriod(year: number, month: number): string {
  const date = new Date(year, month - 1);
  return new Intl.DateTimeFormat('en-GB', {
    month: 'long',
    year: 'numeric',
  }).format(date);
}

export function formatPeriodShort(year: number, month: number): string {
  const date = new Date(year, month - 1);
  return new Intl.DateTimeFormat('en-GB', {
    month: 'short',
    year: '2-digit',
  }).format(date);
}
