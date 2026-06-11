import { useState } from 'react'

export default function Header({ ticker, summary, retraining, onRetrain, addingTicker, addError, onAddTicker, onShowInsights }) {
  const [query, setQuery] = useState('')

  function submit(e) {
    e.preventDefault()
    const value = query.trim()
    if (!value || addingTicker) return
    onAddTicker(value)
    setQuery('')
  }

  return (
    <header className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white">
      {/* logo */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <div className="w-7 h-7 rounded-full bg-gray-900 flex items-center justify-center text-white text-xs font-bold">
          S
        </div>
        <span className="font-semibold text-gray-900 text-sm">StockDash</span>
      </div>

      {/* add ticker */}
      <form
        onSubmit={submit}
        className={`flex items-center gap-2 border rounded px-2.5 py-1 text-xs w-52 mx-6 ${
          addError ? 'border-red-300' : 'border-gray-200'
        }`}
      >
        {addingTicker ? (
          <svg className="w-3 h-3 flex-shrink-0 animate-spin text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        ) : (
          <svg className="w-3 h-3 flex-shrink-0 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        )}
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          disabled={addingTicker}
          placeholder={addError ?? (addingTicker ? 'Adding & training...' : 'Add ticker...')}
          className={`flex-1 min-w-0 outline-none bg-transparent ${
            addError ? 'placeholder-red-400' : 'placeholder-gray-400'
          } text-gray-800`}
        />
      </form>

      {/* ticker summary */}
      <div className="flex items-center gap-3 flex-1 justify-end mr-4">
        {ticker && (
          <>
            <span className="font-semibold text-gray-700 text-sm">{ticker}</span>
            {summary && (
              <>
                <span className="text-gray-900 font-semibold text-sm">${summary.price.toFixed(2)}</span>
                <span className={`text-xs font-medium ${summary.change_pct >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                  {summary.change_pct >= 0 ? '▲' : '▼'} {Math.abs(summary.change_pct).toFixed(2)}% (1d)
                </span>
              </>
            )}
          </>
        )}
      </div>

      {/* insights button */}
      <button
        onClick={onShowInsights}
        className="flex items-center gap-1.5 px-3 py-1.5 mr-2 border border-gray-300 text-gray-700 text-xs rounded hover:bg-gray-50 flex-shrink-0"
      >
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        Insights
      </button>

      {/* retrain button */}
      <button
        onClick={onRetrain}
        disabled={retraining}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-900 text-white text-xs rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
      >
        <svg className={`w-3 h-3 ${retraining ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {retraining ? 'Retraining...' : 'Retrain'}
      </button>
    </header>
  )
}
