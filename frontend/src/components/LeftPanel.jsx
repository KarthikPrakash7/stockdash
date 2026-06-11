const TOOLS = [
  { label: 'Cursor', icon: '↖' },
  { label: 'Draw', icon: '✏' },
  { label: 'Measure', icon: '—' },
  { label: 'Text', icon: 'T' },
]

export default function LeftPanel({ chartData }) {
  const sma5 = chartData?.sma5?.at(-1)?.value
  const sma10 = chartData?.sma10?.at(-1)?.value
  const sma20 = chartData?.sma20?.at(-1)?.value

  return (
    <div className="w-40 flex-shrink-0 border-r border-gray-200 bg-white flex flex-col py-4 px-3 gap-6">
      <section>
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Indicators</p>
        <div className="flex flex-col gap-2">
          <IndicatorRow dot="#8b5cf6" label="SMA 5" value={sma5} />
          <IndicatorRow dot="#f59e0b" label="SMA 10" value={sma10} />
          <IndicatorRow dot="#10b981" label="SMA 20" value={sma20} />
        </div>
      </section>
      <section>
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Tools</p>
        <div className="flex flex-col gap-0.5">
          {TOOLS.map(t => (
            <button
              key={t.label}
              className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-900 py-1 px-1.5 rounded hover:bg-gray-50"
            >
              <span className="w-4 text-center text-gray-400">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}

function IndicatorRow({ dot, label, value }) {
  return (
    <div className="flex items-center justify-between text-xs">
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: dot }} />
        <span className="text-gray-500">{label}</span>
      </div>
      <span className="text-gray-800 font-medium tabular-nums">
        {value != null ? value.toFixed(1) : '—'}
      </span>
    </div>
  )
}
