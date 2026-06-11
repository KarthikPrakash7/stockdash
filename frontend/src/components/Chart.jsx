import { useEffect, useRef } from 'react'
import { createChart, CrosshairMode } from 'lightweight-charts'

export default function Chart({ chartData }) {
  const containerRef = useRef(null)
  const chartRef = useRef(null)
  const seriesRef = useRef({})

  useEffect(() => {
    const chart = createChart(containerRef.current, {
      // TradingView attribution kept in README per lightweight-charts license
      layout: { background: { color: '#ffffff' }, textColor: '#374151', attributionLogo: false },
      grid: { vertLines: { color: '#f3f4f6' }, horzLines: { color: '#f3f4f6' } },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: '#e5e7eb' },
      timeScale: { borderColor: '#e5e7eb', timeVisible: false },
    })

    const observer = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.applyOptions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        })
      }
    })
    observer.observe(containerRef.current)

    const candles = chart.addCandlestickSeries({
      upColor: '#10b981', downColor: '#ef4444',
      borderUpColor: '#10b981', borderDownColor: '#ef4444',
      wickUpColor: '#10b981', wickDownColor: '#ef4444',
    })
    const sma5 = chart.addLineSeries({ color: '#8b5cf6', lineWidth: 1, title: 'SMA 5' })
    const sma10 = chart.addLineSeries({ color: '#f59e0b', lineWidth: 1, title: 'SMA 10' })
    const sma20 = chart.addLineSeries({ color: '#10b981', lineWidth: 1, title: 'SMA 20' })
    const pred = chart.addLineSeries({
      color: '#3b82f6', lineWidth: 2, lineStyle: 2, title: 'Predicted',
    })

    chartRef.current = chart
    seriesRef.current = { candles, sma5, sma10, sma20, pred }

    return () => {
      observer.disconnect()
      chart.remove()
    }
  }, [])

  useEffect(() => {
    const { candles, sma5, sma10, sma20, pred } = seriesRef.current
    if (!candles || !chartData) return

    candles.setData(chartData.ohlcv ?? [])
    sma5.setData(chartData.sma5 ?? [])
    sma10.setData(chartData.sma10 ?? [])
    sma20.setData(chartData.sma20 ?? [])
    pred.setData((chartData.predictions ?? []).map(p => ({ time: p.time, value: p.predicted })))
  }, [chartData])

  return (
    <div className="flex-1 min-w-0 relative bg-white">
      {!chartData && (
        <div className="absolute inset-0 flex items-center justify-center text-gray-400 text-xs">
          Loading chart...
        </div>
      )}
      <div ref={containerRef} className="w-full h-full" />
    </div>
  )
}
