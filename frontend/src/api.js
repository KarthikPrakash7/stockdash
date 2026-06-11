const BASE = '/api'

export async function fetchTickers() {
  const res = await fetch(`${BASE}/tickers`)
  if (!res.ok) throw new Error('Failed to fetch tickers')
  return res.json()
}

export async function fetchChart(ticker) {
  const res = await fetch(`${BASE}/chart/${ticker}`)
  if (!res.ok) throw new Error(`Failed to fetch chart for ${ticker}`)
  return res.json()
}

export async function retrain() {
  const res = await fetch(`${BASE}/retrain`, { method: 'POST' })
  if (!res.ok) throw new Error('Retrain failed')
  return res.json()
}
