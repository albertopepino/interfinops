import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { useAuthStore } from '@/store/authStore';
import type {
  User,
  Site,
  FinancialStatement,
  BudgetEntry,
  DashboardLayout,
  UploadResult,
  PaginatedResponse,
} from '@/types';
import type { KPIResponse } from '@/types/kpi';

// ─── Auth ───────────────────────────────────────────────────────────────────

export function useAuth() {
  const setUser = useAuthStore((s) => s.setUser);
  const clearUser = useAuthStore((s) => s.clearUser);

  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      try {
        const user = await apiClient.get<User>('/auth/me');
        setUser(user);
        return user;
      } catch {
        clearUser();
        return null;
      }
    },
    retry: false,
    staleTime: 10 * 60 * 1000,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: { email: string; password: string }) =>
      apiClient.post<User>('/auth/login', credentials),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth'] });
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const clearUser = useAuthStore((s) => s.clearUser);

  return useMutation({
    mutationFn: () => apiClient.post<void>('/auth/logout'),
    onSuccess: () => {
      clearUser();
      queryClient.clear();
      window.location.href = '/login';
    },
  });
}

// ─── Sites ──────────────────────────────────────────────────────────────────

export function useSites() {
  return useQuery({
    queryKey: ['sites'],
    queryFn: async () => {
      const response = await apiClient.get<{ items: Site[]; total: number }>('/sites');
      return response.items;
    },
  });
}

// ─── Financial Data ─────────────────────────────────────────────────────────

export function useFinancialData(params: {
  siteId: string;
  year: number;
  month: number;
  statementType?: string;
}) {
  return useQuery({
    queryKey: ['financial', params],
    queryFn: () =>
      apiClient.get<FinancialStatement[]>('/financial/statements', {
        site_id: params.siteId,
        year: String(params.year),
        month: String(params.month),
        ...(params.statementType && { statement_type: params.statementType }),
      }),
    enabled: !!params.siteId,
  });
}

// ─── KPIs ───────────────────────────────────────────────────────────────────

export function useSiteKPIs(siteId: string, year: number, month: number) {
  return useQuery({
    queryKey: ['kpis', 'site', siteId, year, month],
    queryFn: () =>
      apiClient.get<KPIResponse>(
        `/kpis/site/${siteId}?period_year=${year}&period_month=${month}`
      ),
    enabled: !!siteId,
  });
}

export function useConsolidatedKPIs(year: number, month: number) {
  return useQuery({
    queryKey: ['kpis', 'consolidated', year, month],
    queryFn: () =>
      apiClient.get<KPIResponse>(
        `/kpis/consolidated?period_year=${year}&period_month=${month}`
      ),
  });
}

export function useMultiMonthKPIs(
  siteId: string,
  year: number,
  months: number[] = [7, 8, 9, 10, 11, 12]
) {
  return useQuery({
    queryKey: ['kpis', 'multi-month', siteId, year, months],
    queryFn: async () => {
      const results = await Promise.all(
        months.map(async (month) => {
          const kpis = await apiClient.get<KPIResponse>(
            `/kpis/site/${siteId}?period_year=${year}&period_month=${month}`
          );
          return { month, kpis };
        })
      );
      return results;
    },
    enabled: !!siteId,
  });
}

export function useConsolidatedMultiMonthKPIs(
  year: number,
  months: number[] = [7, 8, 9, 10, 11, 12]
) {
  return useQuery({
    queryKey: ['kpis', 'consolidated-multi', year, months],
    queryFn: async () => {
      const results = await Promise.all(
        months.map(async (month) => {
          const kpis = await apiClient.get<KPIResponse>(
            `/kpis/consolidated?period_year=${year}&period_month=${month}`
          );
          return { month, kpis };
        })
      );
      return results;
    },
  });
}

// ─── Budget ─────────────────────────────────────────────────────────────────

export function useBudget(params: {
  siteId: string;
  year: number;
}) {
  return useQuery({
    queryKey: ['budget', params],
    queryFn: () =>
      apiClient.get<BudgetEntry[]>('/budget', {
        site_id: params.siteId,
        year: String(params.year),
      }),
    enabled: !!params.siteId,
  });
}

export function useSaveBudget() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { siteId: string; entries: BudgetEntry[] }) =>
      apiClient.put<void>(`/budget/${data.siteId}`, data.entries),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budget'] });
    },
  });
}

// ─── Dashboard Config ───────────────────────────────────────────────────────

export function useDashboardConfig() {
  return useQuery({
    queryKey: ['dashboard', 'config'],
    queryFn: () => apiClient.get<DashboardLayout>('/dashboard/config'),
  });
}

export function useUpdateDashboardConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (layout: DashboardLayout) =>
      apiClient.put<DashboardLayout>('/dashboard/config', layout),
    onSuccess: (data) => {
      queryClient.setQueryData(['dashboard', 'config'], data);
    },
  });
}

// ─── Upload ─────────────────────────────────────────────────────────────────

// ─── Site Statements ───────────────────────────────────────────────────────

export function useSiteStatements(siteId: string, year: number, month: number, type: string) {
  return useQuery({
    queryKey: ['statements', siteId, year, month, type],
    queryFn: () => apiClient.get<{items: any[], total: number}>(
      `/financial-data/site/${siteId}?period_year=${year}&period_month=${month}&statement_type=${type}`
    ),
    enabled: !!siteId,
  });
}

export function useConsolidatedFinancialData(year: number, month: number) {
  return useQuery({
    queryKey: ['financial-data', 'consolidated', year, month],
    queryFn: () => apiClient.get<Record<string, Record<string, string>>>(
      `/financial-data/consolidated?period_year=${year}&period_month=${month}`
    ),
  });
}

// ─── Upload ─────────────────────────────────────────────────────────────────

export function useUploadStatement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      file: File;
      siteId: string;
      statementType: string;
      year: number;
      month: number;
    }) => {
      const formData = new FormData();
      formData.append('file', data.file);
      formData.append('site_id', data.siteId);
      formData.append('statement_type', data.statementType);
      formData.append('year', String(data.year));
      formData.append('month', String(data.month));
      return apiClient.upload<UploadResult>('/upload/statement', formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['financial'] });
      queryClient.invalidateQueries({ queryKey: ['kpis'] });
    },
  });
}

// ─── Targets ──────────────────────────────────────────────────────────────

export function useTargets(siteId: string | null, year: number) {
  return useQuery({
    queryKey: ['targets', siteId, year],
    queryFn: () => {
      const params: Record<string, string> = { period_year: String(year) };
      if (siteId) {
        params.site_id = siteId;
      } else {
        params.overall_only = 'true';
      }
      return apiClient.get<{items: any[], total: number}>('/targets', params);
    },
  });
}

export function useSaveTargets() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (targets: any[]) => apiClient.post('/targets/bulk', targets),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['targets'] }); },
  });
}

// ─── Upload History ───────────────────────────────────────────────────────

export function useUploadHistory(siteId: string) {
  return useQuery({
    queryKey: ['uploads', siteId],
    queryFn: () =>
      apiClient.get<PaginatedResponse<FinancialStatement>>(
        '/upload/history',
        { site_id: siteId }
      ),
    enabled: !!siteId,
  });
}

// ─── Chart of Accounts ──────────────────────────────────────────────────────

export interface GroupAccountResponse {
  id: string;
  code: string;
  name: string;
  account_type: string;
  parent_code: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SiteAccountResponse {
  id: string;
  code: string;
  name: string;
  account_type: string;
  parent_code: string | null;
  display_order: number;
  is_active: boolean;
  site_id: string;
  created_at: string;
  updated_at: string;
}

export interface MappingMatrixEntry {
  site_account: SiteAccountResponse;
  group_account: GroupAccountResponse | null;
}

export interface MappingMatrixResponse {
  site_id: string;
  entries: MappingMatrixEntry[];
  total: number;
}

export function useGroupAccounts() {
  return useQuery({
    queryKey: ['chart-of-accounts', 'group'],
    queryFn: async () => {
      const resp = await apiClient.get<{ items: GroupAccountResponse[]; total: number }>(
        '/chart-of-accounts/group'
      );
      return resp.items;
    },
  });
}

export function useSiteAccounts(siteId: string) {
  return useQuery({
    queryKey: ['chart-of-accounts', 'site', siteId],
    queryFn: async () => {
      const resp = await apiClient.get<{ items: SiteAccountResponse[]; total: number }>(
        `/chart-of-accounts/site/${siteId}`
      );
      return resp.items;
    },
    enabled: !!siteId,
  });
}

export function useAccountMappings(siteId: string) {
  return useQuery({
    queryKey: ['chart-of-accounts', 'mapping', siteId],
    queryFn: () =>
      apiClient.get<MappingMatrixResponse>(`/chart-of-accounts/mapping/${siteId}`),
    enabled: !!siteId,
  });
}

export function useSaveMappings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { siteId: string; mappings: { site_account_id: string; group_account_id: string }[] }) =>
      apiClient.put<MappingMatrixResponse>(
        `/chart-of-accounts/mapping/${data.siteId}`,
        { mappings: data.mappings }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chart-of-accounts'] });
    },
  });
}

export function useUploadGroupCoA() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.upload<{created: number; updated: number; total: number; errors: string[]}>('/chart-of-accounts/group/upload', formData);
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['chart-of-accounts'] }); },
  });
}

export function useUploadSiteCoA() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {siteId: string; file: File}) => {
      const formData = new FormData();
      formData.append('file', data.file);
      return apiClient.upload<{created: number; updated: number; total: number; errors: string[]}>(`/chart-of-accounts/site/${data.siteId}/upload`, formData);
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['chart-of-accounts'] }); },
  });
}
