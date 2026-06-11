const TICKER_COLORS = {
  AAPL: '#3b82f6', MSFT: '#10b981', GOOGL: '#f59e0b', AMZN: '#ef4444', NVDA: '#8b5cf6',
}

export default function BottomTabs({ tabs, activeTicker, onSelect, onClose }) {
  return (
    <div className="flex items-center border-t border-gray-200 bg-white px-2 py-1 gap-1">
      {tabs.map(ticker => (
        <button
          key={ticker}
          onClick={() => onSelect(ticker)}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            activeTicker === ticker
              ? 'bg-gray-100 text-gray-900'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
          }`}
        >
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ background: TICKER_COLORS[ticker] ?? '#6b7280' }}
          />
          {ticker}
          <span
            role="button"
            onClick={e => { e.stopPropagation(); onClose(ticker) }}
            className="text-gray-400 hover:text-gray-700 leading-none ml-0.5"
          >
            ×
          </span>
        </button>
      ))}
    </div>
  )
}
