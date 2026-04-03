import { useMemo } from 'react';
import Chart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';

interface BarConfig {
  dataKey: string;
  name: string;
  color: string;
}

interface BarChartProps {
  data: Array<Record<string, unknown>>;
  bars: BarConfig[];
  xAxisKey: string;
}

export function FinancialBarChart({ data, bars, xAxisKey }: BarChartProps) {
  const { series, options } = useMemo(() => {
    const cats = data.map((d) => String(d[xAxisKey]));

    const allSeries: any[] = bars.map((bar) => ({
      name: bar.name,
      data: data.map((d) => Number(d[bar.dataKey]) || 0),
    }));

    const colors = bars.map((b) => b.color);

    const fmt = (val: number) => {
      if (Math.abs(val) >= 1e6) return `€${(val / 1e6).toFixed(1)}M`;
      if (Math.abs(val) >= 1e3) return `€${(val / 1e3).toFixed(0)}K`;
      return `€${val.toFixed(0)}`;
    };

    const opts: ApexOptions = {
      chart: {
        type: 'bar',
        toolbar: { show: false },
        animations: { enabled: true, speed: 600 },
        fontFamily: 'Inter, system-ui, sans-serif',
        background: 'transparent',
      },
      colors,
      plotOptions: {
        bar: {
          borderRadius: 6,
          borderRadiusApplication: 'end',
          columnWidth: '55%',
        },
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'light',
          type: 'vertical',
          shadeIntensity: 0.2,
          opacityFrom: 1,
          opacityTo: 0.85,
          stops: [0, 100],
        },
      },
      dataLabels: { enabled: false },
      grid: {
        borderColor: 'rgba(148,163,184,0.1)',
        strokeDashArray: 4,
        xaxis: { lines: { show: false } },
      },
      xaxis: {
        categories: cats,
        axisBorder: { show: false },
        axisTicks: { show: false },
        labels: { style: { colors: '#94a3b8', fontSize: '11px', fontWeight: 500 } },
      },
      yaxis: {
        labels: {
          style: { colors: '#94a3b8', fontSize: '11px', fontWeight: 500 },
          formatter: fmt,
        },
      },
      tooltip: {
        theme: 'light',
        y: { formatter: fmt },
        style: { fontSize: '12px' },
      },
      legend: {
        show: bars.length > 1,
        position: 'bottom',
        fontSize: '12px',
        fontWeight: 500,
        labels: { colors: '#64748b' },
        markers: { size: 4, shape: 'circle' as const },
      },
    };

    return { series: allSeries, options: opts };
  }, [data, bars, xAxisKey]);

  return (
    <div className="w-full">
      <Chart options={options} series={series} type="bar" height={280} />
    </div>
  );
}
