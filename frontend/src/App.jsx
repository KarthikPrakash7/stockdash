import { useState, useEffect } from 'react'
import { fetchTickers, fetchChart, retrain } from './api'
import Header from './components/Header'
import LeftPanel from './components/LeftPanel'
import Chart from './components/Chart'
import RightPanel from './components/RightPanel'
import BottomTabs from './components/BottomTabs'

export default function App() {
  const [tickers, setTickers] = useState([])
  const [openTabs, setOpenTabs] = useState(['AAPL'])
  const [activeTicker, setActiveTicker] = useState('AAPL')
  const [chartData, setChartData] = useState(null)
  const [retraining, setRetraining] = useState(false)

  useEffect(() => {
    fetchTickers().then(setTickers).catch(console.error)
  }, [])

  useEffect(() => {
    if (!activeTicker) return
    setChartData(null)
    fetchChart(activeTicker).then(setChartData).catch(console.error)
  }, [activeTicker])

  function selectTicker(ticker) {
    setActiveTicker(ticker)
    if (!openTabs.includes(ticker)) setOpenTabs(prev => [...prev, ticker])
  }

  function closeTab(ticker) {
    const next = openTabs.filter(t => t !== ticker)
    setOpenTabs(next)
    if (activeTicker === ticker) setActiveTicker(next[next.length - 1] ?? null)
  }

  async function handleRetrain() {
    setRetraining(true)
    try {
      await retrain()
      const [updatedTickers, updatedChart] = await Promise.all([
        fetchTickers(),
        activeTicker ? fetchChart(activeTicker) : Promise.resolve(null),
      ])
      setTickers(updatedTickers)
      if (updatedChart) setChartData(updatedChart)
    } finally {
      setRetraining(false)
    }
  }

  const activeTickerSummary = tickers.find(t => t.ticker === activeTicker)

  return (
    <div className="flex flex-col h-screen bg-white font-sans text-sm select-none">
      <Header
        ticker={activeTicker}
        summary={activeTickerSummary}
        retraining={retraining}
        onRetrain={handleRetrain}
      />
      <div className="flex flex-col flex-1 min-h-0">
        {/* ticker info bar */}
        <div className="flex items-center gap-4 px-4 py-1 border-b border-gray-200 text-xs text-gray-600">
          {activeTicker && (
            <>
              <span className="font-semibold text-gray-800">{activeTicker}</span>
              <span className="text-gray-300">·</span>
              <span>Nasdaq</span>
              {chartData?.ohlcv?.length > 0 && (() => {
                const last = chartData.ohlcv[chartData.ohlcv.length - 1]
                return (
                  <>
                    <span>O {last.open.toFixed(2)}</span>
                    <span>H {last.high.toFixed(2)}</span>
                    <span>L {last.low.toFixed(2)}</span>
                    <span>C {last.close.toFixed(2)}</span>
                  </>
                )
              })()}
              {chartData?.tomorrow_pred != null && (
                <span className="ml-auto text-blue-600 font-semibold">
                  AI Next-day: ${chartData.tomorrow_pred.toFixed(2)}
                </span>
              )}
            </>
          )}
        </div>
        {/* main content row */}
        <div className="flex flex-1 min-h-0">
          <LeftPanel chartData={chartData} />
          <Chart chartData={chartData} />
          <RightPanel
            tickers={tickers}
            activeTicker={activeTicker}
            chartData={chartData}
            onSelectTicker={selectTicker}
          />
        </div>
      </div>
      <BottomTabs
        tabs={openTabs}
        activeTicker={activeTicker}
        tickers={tickers}
        onSelect={setActiveTicker}
        onClose={closeTab}
      />
    </div>
  )
}
