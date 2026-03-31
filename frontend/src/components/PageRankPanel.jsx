import { useState, useEffect } from 'react'
import { fetchPageRank } from '../services/api'

export default function PageRankPanel({ onSelectWallet }) {
  const [rankings, setRankings] = useState([])
  const [loading, setLoading]   = useState(false)

  useEffect(() => {
    setLoading(true)
    fetchPageRank()
      .then(d => setRankings(d.rankings || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-9 bg-white/5 rounded-lg animate-pulse" />
        ))}
      </div>
    )
  }

  const max = rankings[0]?.pagerank || 1

  return (
    <div className="space-y-2">
      <p className="text-xs text-white/40">Top wallets by network centrality</p>
      {rankings.map((r, i) => {
        const pct = (r.pagerank / max) * 100
        const isHigh = r.pagerank > max * 0.7
        return (
          <button
            key={r.address}
            onClick={() => onSelectWallet && onSelectWallet(r.address)}
            className="w-full text-left bg-white/5 hover:bg-white/8 border border-white/10 rounded-lg px-3 py-2 transition-colors group"
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs text-white/30 w-4">#{i + 1}</span>
                <span className="font-mono text-xs text-white/70 group-hover:text-white/90 truncate max-w-[140px]">
                  {r.address}
                </span>
              </div>
              <span className={`text-xs font-mono ${isHigh ? 'text-red-400' : 'text-white/40'}`}>
                {r.pagerank.toFixed(3)}
              </span>
            </div>
            <div className="h-1 bg-white/10 rounded-full">
              <div
                className={`h-full rounded-full ${isHigh ? 'bg-red-500' : 'bg-accent'}`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </button>
        )
      })}
    </div>
  )
}
