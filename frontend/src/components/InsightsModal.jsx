import { useEffect, useState } from 'react'
import { fetchInsights } from '../api'

export default function InsightsModal({ onClose, onSelectTicker }) {
  const [insights, setInsights] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchInsights()
      .then(data => setInsights(data.insights))
      .catch(err => setError(err.message))
  }, [])

  return (
    <div
      className="fixed inset-0 bg-black/30 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl w-[480px] max-h-[70vh] flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-900">Insights — hot stocks on your watchlist</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-sm">✕</button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {error && <p className="p-4 text-xs text-red-500">{error}</p>}
          {!insights && !error && <p className="p-4 text-xs text-gray-400">Crunching numbers...</p>}
          {insights?.map((item, i) => (
            <button
              key={item.ticker}
              onClick={() => { onSelectTicker(item.ticker); onClose() }}
              className="w-full text-left px-4 py-3 border-b border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs text-gray-400 w-4">{i + 1}.</span>
                <span className="text-sm font-semibold text-gray-900">{item.ticker}</span>
                <span
                  className={`ml-auto text-xs font-semibold tabular-nums px-1.5 py-0.5 rounded ${
                    item.score >= 0 ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {item.score >= 0 ? '+' : ''}{item.score.toFixed(2)}
                </span>
              </div>
              <p className="text-xs text-gray-500 ml-6">{item.reason}</p>
            </button>
          ))}
          {insights?.length === 0 && (
            <p className="p-4 text-xs text-gray-400">No data yet — add tickers or run a retrain first.</p>
          )}
        </div>

        <p className="px-4 py-2 text-[10px] text-gray-400 border-t border-gray-100">
          Composite of momentum, volume, news sentiment, and model signal. Not financial advice.
        </p>
      </div>
    </div>
  )
}
