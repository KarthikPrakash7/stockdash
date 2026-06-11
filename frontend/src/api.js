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

export async function addToWatchlist(ticker) {
  const res = await fetch(`${BASE}/watchlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticker }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `Failed to add ${ticker}`)
  }
  return res.json()
}

export async function fetchInsights() {
  const res = await fetch(`${BASE}/insight`)
  if (!res.ok) throw new Error('Failed to fetch insights')
  return res.json()
}

export async function removeFromWatchlist(ticker) {
  const res = await fetch(`${BASE}/watchlist/${ticker}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`Failed to remove ${ticker}`)
  return res.json()
}
