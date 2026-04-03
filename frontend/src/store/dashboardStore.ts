import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CurrencyDisplayMode, Theme, DashboardLayoutItem } from '@/types';
import type { Language } from '@/i18n/translations';

const DEFAULT_VISIBLE_KPIS = [
  'revenue', 'gross-margin', 'ebitda', 'net-margin',
  'current-ratio', 'working-capital', 'debt-equity', 'cash',
];

const DEFAULT_VISIBLE_WIDGETS = [
  'revenue-trend', 'profitability', 'working-capital',
  'ar-ap', 'cash-flow', 'expense-breakdown',
];

interface DashboardState {
  layout: DashboardLayoutItem[];
  selectedSiteId: string | null;
  selectedYear: number;
  selectedMonth: number;
  currencyMode: CurrencyDisplayMode;
  theme: Theme;
  language: Language;
  sidebarCollapsed: boolean;
  visibleKPIs: string[];
  visibleWidgets: string[];

  setLayout: (layout: DashboardLayoutItem[]) => void;
  setSelectedSite: (siteId: string) => void;
  setSelectedPeriod: (year: number, month: number) => void;
  setCurrencyMode: (mode: CurrencyDisplayMode) => void;
  toggleCurrencyMode: () => void;
  setLanguage: (lang: Language) => void;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setVisibleKPIs: (ids: string[]) => void;
  setVisibleWidgets: (ids: string[]) => void;
}

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set) => ({
      layout: [],
      selectedSiteId: null,
      selectedYear: 2025,
      selectedMonth: 12,
      currencyMode: 'EUR',
      theme: 'light',
      language: 'en' as Language,
      sidebarCollapsed: false,
      visibleKPIs: DEFAULT_VISIBLE_KPIS,
      visibleWidgets: DEFAULT_VISIBLE_WIDGETS,

      setLayout: (layout) => set({ layout }),

      setSelectedSite: (siteId) => set({ selectedSiteId: siteId }),

      setSelectedPeriod: (year, month) =>
        set({ selectedYear: year, selectedMonth: month }),

      setCurrencyMode: (mode) => set({ currencyMode: mode }),

      toggleCurrencyMode: () =>
        set((state) => ({
          currencyMode: state.currencyMode === 'EUR' ? 'local' : 'EUR',
        })),

      setTheme: (theme) => {
        if (theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        return set({ theme });
      },

      toggleTheme: () =>
        set((state) => {
          const newTheme = state.theme === 'light' ? 'dark' : 'light';
          if (newTheme === 'dark') {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { theme: newTheme };
        }),

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setLanguage: (language) => set({ language }),
      setVisibleKPIs: (ids) => set({ visibleKPIs: ids }),
      setVisibleWidgets: (ids) => set({ visibleWidgets: ids }),
    }),
    {
      name: 'interfinops-dashboard',
      version: 6,
      partialize: (state) => ({
        selectedSiteId: state.selectedSiteId,
        selectedYear: state.selectedYear,
        selectedMonth: state.selectedMonth,
        currencyMode: state.currencyMode,
        theme: state.theme,
        language: state.language,
        sidebarCollapsed: state.sidebarCollapsed,
        visibleKPIs: state.visibleKPIs,
        visibleWidgets: state.visibleWidgets,
      }),
    }
  )
);
