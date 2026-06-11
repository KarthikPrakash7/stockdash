export default function Header({ ticker, summary, retraining, onRetrain }) {
  return (
    <header className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white">
      {/* logo */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <div className="w-7 h-7 rounded-full bg-gray-900 flex items-center justify-center text-white text-xs font-bold">
          S
        </div>
        <span className="font-semibold text-gray-900 text-sm">StockDash</span>
      </div>

      {/* search */}
      <div className="flex items-center gap-2 border border-gray-200 rounded px-2.5 py-1 text-gray-400 text-xs w-44 mx-6">
        <svg className="w-3 h-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <span>Search ticker...</span>
      </div>

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
