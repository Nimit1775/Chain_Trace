import { useState } from 'react'
import { fetchShortestPath } from '../services/api'

export default function PathTracer({ onPathFound }) {
  const [source, setSource] = useState('')
  const [target, setTarget] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  const trace = async () => {
    if (!source.trim() || !target.trim()) return
    setLoading(true); setError(null); setResult(null)
    try {
      const data = await fetchShortestPath(source.trim(), target.trim())
      setResult(data)
      onPathFound && onPathFound(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Path not found')
    } finally {
      setLoading(false)
    }
  }

  const DEMO_PAIRS = [
    { label: 'Entry → Mixer',   src: '0xENTRY0001', tgt: '0xMIXER0001' },
    { label: 'Ring A start → end', src: '0xRINGA0001', tgt: '0xRINGA0007' },
    { label: 'Legit → Mixer',   src: '0xLEGIT0001', tgt: '0xMIXER0001' },
  ]

  return (
    <div className="space-y-3">
      <div className="space-y-2">
        <input
          value={source}
          onChange={e => setSource(e.target.value)}
          placeholder="Source wallet…"
          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-white/25 focus:outline-none focus:border-accent"
        />
        <div className="flex items-center gap-2">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-xs text-white/20">to</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>
        <input
          value={target}
          onChange={e => setTarget(e.target.value)}
          placeholder="Target wallet…"
          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-white/25 focus:outline-none focus:border-accent"
        />
      </div>

      {/* Demo pairs */}
      <div className="flex flex-wrap gap-1">
        {DEMO_PAIRS.map(p => (
          <button
            key={p.label}
            onClick={() => { setSource(p.src); setTarget(p.tgt) }}
            className="text-xs px-2 py-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded text-white/40 hover:text-white/70 transition-colors"
          >{p.label}</button>
        ))}
      </div>

      <button
        onClick={trace}
        disabled={loading || !source.trim() || !target.trim()}
        className="w-full py-2 bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/40 text-orange-400 text-xs font-semibold rounded-lg transition-all disabled:opacity-40"
      >
        {loading ? 'Tracing path…' : 'Trace shortest path'}
      </button>

      {error && (
        <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded p-2">{error}</p>
      )}

      {result && result.path?.length > 0 && (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 space-y-2">
          <p className="text-xs text-orange-400 font-semibold">{result.path.length} hops found</p>
          <div className="space-y-1">
            {result.path.map((addr, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-orange-500/30 border border-orange-500/50 flex items-center justify-center text-orange-400 text-xs flex-shrink-0">{i + 1}</span>
                <span className="font-mono text-xs text-white/70 truncate">{addr}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
