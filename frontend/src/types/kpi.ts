export interface KPIValue {
  name: string;
  value: string | null;
  unit: 'currency' | 'percentage' | 'ratio' | 'days';
  description: string;
}

export interface KPIResponse {
  site_id: string | null;
  site_name: string | null;
  period_year: number;
  period_month: number;
  currency: string;
  profitability: KPIValue[];
  liquidity: KPIValue[];
  efficiency: KPIValue[];
  leverage: KPIValue[];
}

export interface KPICardData {
  id: string;
  label: string;
  value: number;
  formattedValue: string;
  changePercent?: number;
  changeDirection?: 'up' | 'down' | 'flat';
  isPositiveGood: boolean;
  benchmark?: number;
  unit: 'currency' | 'percent' | 'ratio' | 'days';
  icon?: string;
  color?: string;
}
