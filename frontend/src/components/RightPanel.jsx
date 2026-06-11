import { useState } from 'react'

const TICKER_COLORS = {
  AAPL: '#3b82f6', MSFT: '#10b981', GOOGL: '#f59e0b', AMZN: '#ef4444', NVDA: '#8b5cf6',
}

function calcMAE(predictions) {
  if (!predictions?.length) return null
  return predictions.reduce((s, p) => s + Math.abs(p.actual - p.predicted), 0) / predictions.length
}

function calcRMSE(predictions) {
  if (!predictions?.length) return null
  return Math.sqrt(predictions.reduce((s, p) => s + (p.actual - p.predicted) ** 2, 0) / predictions.length)
}

export default function RightPanel({ tickers, activeTicker, chartData, onSelectTicker, onRemoveTicker }) {
  const [tab, setTab] = useState('Watchlist')
  const summary = tickers.find(t => t.ticker === activeTicker)
  const mae = calcMAE(chartData?.predictions)
  const rmse = calcRMSE(chartData?.predictions)

  return (
    <div className="w-56 flex-shrink-0 border-l border-gray-200 bg-white flex flex-col">
      {/* tab strip */}
      <div className="flex border-b border-gray-200">
        {['Watchlist', 'Alerts', 'Models'].map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2 text-xs font-medium transition-colors ${
              tab === t
                ? 'border-b-2 border-gray-900 text-gray-900'
                : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* tab content */}
      <div className="flex-1 overflow-y-auto">
        {tab === 'Watchlist' && tickers.map(t => (
          <div
            key={t.ticker}
            onClick={() => onSelectTicker(t.ticker)}
            className={`group w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 transition-colors cursor-pointer ${
              activeTicker === t.ticker ? 'bg-gray-50' : ''
            }`}
          >
            <div className="flex items-center gap-2">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ background: TICKER_COLORS[t.ticker] ?? '#6b7280' }}
              />
              <span className="text-xs font-semibold text-gray-800">{t.ticker}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="text-right">
                <div className="text-xs font-semibold text-gray-900 tabular-nums">{t.price.toFixed(2)}</div>
                <div className={`text-xs tabular-nums ${t.change_pct >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                  {t.change_pct >= 0 ? '+' : ''}{t.change_pct.toFixed(1)}%
                </div>
              </div>
              <button
                onClick={e => { e.stopPropagation(); onRemoveTicker(t.ticker) }}
                title={`Remove ${t.ticker}`}
                className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-500 text-xs px-0.5 transition-opacity"
              >
                ✕
              </button>
            </div>
          </div>
        ))}
        {tab !== 'Watchlist' && (
          <p className="p-4 text-xs text-gray-400">Coming in a future milestone.</p>
        )}
      </div>

      {/* ticker detail card */}
      {summary && (
        <div className="border-t border-gray-200 p-3 flex-shrink-0">
          <div className="font-semibold text-gray-900 text-sm">{summary.ticker}</div>
          <div className="text-xs text-gray-400 mb-2">Nasdaq</div>
          <div className="flex items-baseline gap-1 mb-0.5">
            <span className="text-xl font-bold text-gray-900">${summary.price.toFixed(2)}</span>
            <span className="text-xs text-gray-400">USD</span>
          </div>
          <div className={`text-xs font-medium mb-3 ${summary.change_pct >= 0 ? 'text-green-600' : 'text-red-500'}`}>
            {summary.change_pct >= 0 ? '▲' : '▼'} {Math.abs(summary.change_pct).toFixed(2)}%
          </div>
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Model</div>
          <MetricRow
            label="Pred. next close"
            value={chartData?.tomorrow_pred != null ? `$${chartData.tomorrow_pred.toFixed(2)}` : '—'}
            highlight
          />
          <MetricRow label="MAE" value={mae != null ? mae.toFixed(2) : '—'} />
          <MetricRow label="RMSE" value={rmse != null ? rmse.toFixed(2) : '—'} />
        </div>
      )}
    </div>
  )
}

function MetricRow({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-xs text-gray-500">{label}</span>
      <span className={`text-xs font-semibold tabular-nums ${highlight ? 'text-blue-600' : 'text-gray-800'}`}>
        {value}
      </span>
    </div>
  )
}
