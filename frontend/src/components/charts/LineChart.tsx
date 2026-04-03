import { useMemo } from 'react';
import Chart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';

interface LineChartProps {
  data: Array<Record<string, unknown>>;
  dataKey: string;
  xAxisKey: string;
  color?: string;
  additionalLines?: Array<{
    dataKey: string;
    name: string;
    color: string;
    dashed?: boolean;
  }>;
  isCurrency?: boolean;
  showLegend?: boolean;
}

export function FinancialLineChart({
  data,
  dataKey,
  xAxisKey,
  color = '#3b82f6',
  additionalLines = [],
  isCurrency = true,
  showLegend = false,
}: LineChartProps) {
  const { series, options } = useMemo(() => {
    const cats = data.map((d) => String(d[xAxisKey]));

    const allSeries: any[] = [
      {
        name: dataKey,
        data: data.map((d) => Number(d[dataKey]) || 0),
      },
      ...additionalLines.map((line) => ({
        name: line.name,
        data: data.map((d) => Number(d[line.dataKey]) || 0),
      })),
    ];

    const colors = [color, ...additionalLines.map((l) => l.color)];

    const dashArray = [0, ...additionalLines.map((l) => (l.dashed ? 5 : 0))];

    const fmt = (val: number) => {
      if (isCurrency) {
        if (Math.abs(val) >= 1e6) return `${(val / 1e6).toFixed(1)}M`;
        if (Math.abs(val) >= 1e3) return `${(val / 1e3).toFixed(0)}K`;
        return val.toFixed(0);
      }
      return val.toFixed(1);
    };

    const opts: ApexOptions = {
      chart: {
        type: 'area',
        toolbar: { show: false },
        zoom: { enabled: false },
        animations: { enabled: true, speed: 600 },
        fontFamily: 'Inter, system-ui, sans-serif',
        background: 'transparent',
      },
      colors,
      stroke: { curve: 'smooth', width: 2.5, dashArray },
      fill: {
        type: 'gradient',
        gradient: {
          shadeIntensity: 1,
          opacityFrom: 0.25,
          opacityTo: 0.02,
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
        y: { formatter: (val: number) => (isCurrency ? `€${fmt(val)}` : `${val.toFixed(1)}%`) },
        style: { fontSize: '12px' },
      },
      legend: {
        show: showLegend,
        position: 'bottom',
        fontSize: '12px',
        fontWeight: 500,
        labels: { colors: '#64748b' },
        markers: { size: 4, shape: 'circle' as const },
        itemMargin: { horizontal: 12 },
      },
      markers: { size: 4, strokeWidth: 0, hover: { size: 6 } },
    };

    return { series: allSeries, categories: cats, options: opts };
  }, [data, dataKey, xAxisKey, color, additionalLines, isCurrency, showLegend]);

  return (
    <div className="w-full">
      <Chart options={options} series={series} type="area" height={280} />
    </div>
  );
}
