import { useDashboardStore } from '@/store/dashboardStore';
import translations from './translations';

export function useTranslation() {
  const language = useDashboardStore((s) => s.language);

  function t(key: string): string {
    return translations[language]?.[key] || translations.en[key] || key;
  }

  return { t, language };
}
