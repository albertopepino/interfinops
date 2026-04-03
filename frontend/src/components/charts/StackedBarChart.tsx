import { useMemo } from 'react';
import Chart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';

interface StackedBarConfig {
  dataKey: string;
  name: string;
  color: string;
}

interface StackedBarChartProps {
  data: Array<Record<string, unknown>>;
  bars: StackedBarConfig[];
  xAxisKey: string;
}

export function StackedBarChart({ data, bars, xAxisKey }: StackedBarChartProps) {
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
        stacked: true,
        toolbar: { show: false },
        animations: { enabled: true, speed: 600 },
        fontFamily: 'Inter, system-ui, sans-serif',
        background: 'transparent',
      },
      colors,
      plotOptions: {
        bar: {
          borderRadius: 4,
          borderRadiusApplication: 'end',
          borderRadiusWhenStacked: 'last',
          columnWidth: '50%',
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
        position: 'bottom',
        fontSize: '12px',
        fontWeight: 500,
        labels: { colors: '#64748b' },
        markers: { size: 4, shape: 'circle' as const },
        itemMargin: { horizontal: 12 },
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
