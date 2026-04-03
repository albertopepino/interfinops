export type Role = 'admin' | 'group_cfo' | 'local_cfo';

export type Currency = 'EUR' | 'USD' | 'GBP' | 'CHF' | 'SEK' | 'NOK' | 'DKK' | 'PLN' | 'CZK' | 'HUF' | 'RON';

export type CurrencyDisplayMode = 'local' | 'EUR';

export type Theme = 'light' | 'dark';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  assigned_site_ids: string[];
}

export interface Site {
  id: string;
  name: string;
  country: string;
  local_currency: string;
  is_active: boolean;
  created_at: string;
}

export interface Period {
  year: number;
  month: number;
  label: string;
}

export type StatementType = 'income_statement' | 'balance_sheet' | 'cash_flow';

export interface FinancialStatement {
  id: string;
  siteId: string;
  statementType: StatementType;
  period: Period;
  currency: Currency;
  uploadedBy: string;
  uploadedAt: string;
  status: 'pending' | 'validated' | 'approved' | 'rejected';
  lineItems: LineItem[];
}

export interface LineItem {
  id: string;
  statementId: string;
  accountCode: string;
  accountName: string;
  category: string;
  subcategory: string;
  amount: number;
  amountEUR: number;
  notes?: string;
}

export interface BudgetEntry {
  id: string;
  siteId: string;
  accountCode: string;
  accountName: string;
  category: string;
  period: Period;
  budgetAmount: number;
  budgetAmountEUR: number;
  actualAmount?: number;
  actualAmountEUR?: number;
  varianceAmount?: number;
  variancePercent?: number;
}

export interface DashboardWidget {
  id: string;
  type: 'kpi_card' | 'line_chart' | 'bar_chart' | 'combo_chart' | 'stacked_bar' | 'table';
  title: string;
  dataSource: string;
  config: Record<string, unknown>;
}

export interface DashboardLayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
}

export interface DashboardLayout {
  id: string;
  userId: string;
  widgets: DashboardWidget[];
  layout: DashboardLayoutItem[];
}

export interface UploadResult {
  success: boolean;
  statementId?: string;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  lineItemCount: number;
}

export interface ValidationError {
  row?: number;
  field: string;
  message: string;
}

export interface ValidationWarning {
  row?: number;
  field: string;
  message: string;
}

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
