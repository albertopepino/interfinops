import { useMemo } from 'react';
import Chart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';

interface ComboChartProps {
  data: Array<Record<string, unknown>>;
  barKey: string;
  barName: string;
  barColor: string;
  lineKey: string;
  lineName: string;
  lineColor: string;
  xAxisKey: string;
}

export function ComboChart({
  data, barKey, barName, barColor,
  lineKey, lineName, lineColor, xAxisKey,
}: ComboChartProps) {
  const { series, options } = useMemo(() => {
    const cats = data.map((d) => String(d[xAxisKey]));

    const allSeries: any[] = [
      { name: barName, type: 'column', data: data.map((d) => Number(d[barKey]) || 0) },
      { name: lineName, type: 'line', data: data.map((d) => Number(d[lineKey]) || 0) },
    ];

    const opts: ApexOptions = {
      chart: {
        type: 'line',
        toolbar: { show: false },
        animations: { enabled: true, speed: 600 },
        fontFamily: 'Inter, system-ui, sans-serif',
        background: 'transparent',
      },
      colors: [barColor, lineColor],
      stroke: { width: [0, 3], curve: 'smooth' },
      plotOptions: {
        bar: {
          borderRadius: 5,
          borderRadiusApplication: 'end',
          columnWidth: '50%',
        },
      },
      fill: {
        type: ['gradient', 'solid'],
        gradient: {
          shade: 'light',
          type: 'vertical',
          shadeIntensity: 0.15,
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
          formatter: (val: number) => val.toFixed(2),
        },
      },
      tooltip: {
        theme: 'light',
        shared: true,
        intersect: false,
        y: { formatter: (val: number) => val.toFixed(2) + 'x' },
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
      markers: { size: [0, 4], strokeWidth: 0, hover: { size: 6 } },
    };

    return { series: allSeries, options: opts };
  }, [data, barKey, barName, barColor, lineKey, lineName, lineColor, xAxisKey]);

  return (
    <div className="w-full">
      <Chart options={options} series={series} type="line" height={280} />
    </div>
  );
}
