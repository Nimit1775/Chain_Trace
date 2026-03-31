import { useState } from 'react'

const DEMO_ADDRESSES = [
  { label: 'Entry wallet (connected to fraud ring)', address: '0xENTRY0001' },
  { label: 'Fraud ring node A', address: '0xRINGA0001' },
  { label: 'Mixer wallet', address: '0xMIXER0001' },
  { label: 'Legit wallet', address: '0xLEGIT0001' },
]

export default function SearchBar({ onSearch, loading }) {
  const [value, setValue] = useState('')
  const [showDemos, setShowDemos] = useState(false)

  const submit = (addr) => {
    const a = (addr || value).trim()
    if (!a) return
    setValue(a)
    setShowDemos(false)
    onSearch(a)
  }

  return (
    <div className="relative flex-1 max-w-2xl">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-sm font-mono">⬡</span>
          <input
            type="text"
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && submit()}
            onFocus={() => setShowDemos(true)}
            onBlur={() => setTimeout(() => setShowDemos(false), 150)}
            placeholder="Enter wallet address… e.g. 0xENTRY0001"
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-8 pr-4 py-2.5 text-sm font-mono text-white placeholder-white/25 focus:outline-none focus:border-accent focus:bg-white/8 transition-all"
          />
          {showDemos && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-[#1a1d26] border border-white/10 rounded-lg overflow-hidden z-50 shadow-xl">
              <p className="text-xs text-white/40 px-3 pt-2 pb-1 uppercase tracking-wider">Demo addresses</p>
              {DEMO_ADDRESSES.map(d => (
                <button
                  key={d.address}
                  onMouseDown={() => submit(d.address)}
                  className="w-full text-left px-3 py-2 hover:bg-white/5 transition-colors"
                >
                  <p className="text-xs font-mono text-accent">{d.address}</p>
                  <p className="text-xs text-white/40 mt-0.5">{d.label}</p>
                </button>
              ))}
            </div>
          )}
        </div>
        <button
          onClick={() => submit()}
          disabled={loading || !value.trim()}
          className="px-5 py-2.5 bg-accent hover:bg-accent/80 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg transition-all"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeDasharray="32" strokeDashoffset="12"/>
              </svg>
              Tracing…
            </span>
          ) : 'Trace'}
        </button>
      </div>
    </div>
  )
}
