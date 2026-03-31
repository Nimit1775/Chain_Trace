const CLUSTER_COLORS = [
  { bg: 'bg-purple-500/10', border: 'border-purple-500/25', text: 'text-purple-400', dot: 'bg-purple-500' },
  { bg: 'bg-pink-500/10',   border: 'border-pink-500/25',   text: 'text-pink-400',   dot: 'bg-pink-500' },
  { bg: 'bg-cyan-500/10',   border: 'border-cyan-500/25',   text: 'text-cyan-400',   dot: 'bg-cyan-500' },
  { bg: 'bg-amber-500/10',  border: 'border-amber-500/25',  text: 'text-amber-400',  dot: 'bg-amber-500' },
]

export default function ClustersPanel({ clusters, onSelectWallet }) {
  if (!clusters || clusters.length === 0) {
    return (
      <div className="text-center py-6 text-white/20">
        <p className="text-xs">No clusters detected yet</p>
        <p className="text-xs mt-1">Search a wallet first</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-white/40">
        {clusters.length} suspected fraud {clusters.length === 1 ? 'ring' : 'rings'} detected
      </p>
      {clusters.map((cluster, i) => {
        const color = CLUSTER_COLORS[i % CLUSTER_COLORS.length]
        return (
          <div key={cluster.cluster_id} className={`${color.bg} border ${color.border} rounded-lg p-3 space-y-2`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${color.dot} animate-pulse`} />
                <span className={`text-xs font-semibold ${color.text}`}>
                  Cluster #{cluster.cluster_id}
                </span>
              </div>
              <span className="text-xs text-white/30">{cluster.size} wallets</span>
            </div>
            <div className="space-y-1">
              {cluster.wallets.slice(0, 5).map(addr => (
                <button
                  key={addr}
                  onClick={() => onSelectWallet && onSelectWallet(addr)}
                  className="block w-full text-left font-mono text-xs text-white/50 hover:text-white/90 hover:bg-white/5 rounded px-1 py-0.5 transition-colors truncate"
                >
                  {addr}
                </button>
              ))}
              {cluster.wallets.length > 5 && (
                <p className="text-xs text-white/20 px-1">
                  +{cluster.wallets.length - 5} more wallets
                </p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
