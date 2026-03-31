import RiskBadge from './RiskBadge'

function Stat({ label, value, mono = false }) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-white/5">
      <span className="text-xs text-white/40">{label}</span>
      <span className={`text-xs text-white/80 ${mono ? 'font-mono' : ''}`}>{value ?? '—'}</span>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div className="mb-4">
      <p className="text-xs uppercase tracking-widest text-white/30 mb-2">{title}</p>
      {children}
    </div>
  )
}

export default function Sidebar({ selected, report, reportLoading, onInvestigate, clusters }) {
  const isWallet = selected?.type === 'wallet'

  if (!selected) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-white/20 p-6 select-none">
        <div className="text-4xl mb-3">◎</div>
        <p className="text-xs text-center">Click any node to inspect it</p>
      </div>
    )
  }

  // Find which cluster this wallet belongs to
  const walletCluster = clusters?.find(c => c.wallets.includes(selected.id))

  return (
    <div className="flex flex-col h-full overflow-y-auto p-4 gap-4">

      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className={`w-2 h-2 rounded-full ${selected.flagged ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
          <span className="text-xs text-white/40 uppercase tracking-wider">
            {isWallet ? 'Wallet' : 'Transaction'}
          </span>
          {selected.flagged && (
            <span className="ml-auto text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded">
              FLAGGED
            </span>
          )}
        </div>
        <p className="font-mono text-xs text-white/60 break-all leading-relaxed">{selected.id}</p>
      </div>

      {/* Risk score */}
      {isWallet && selected.risk_score != null && (
        <Section title="Risk Score">
          <RiskBadge score={selected.risk_score} />
        </Section>
      )}

      {/* Wallet stats */}
      {isWallet && (
        <Section title="Wallet Details">
          <Stat label="Transactions" value={selected.tx_count} />
          <Stat label="Total sent"   value={selected.total_sent != null ? `$${Number(selected.total_sent).toLocaleString()}` : null} />
          <Stat label="Total received" value={selected.total_received != null ? `$${Number(selected.total_received).toLocaleString()}` : null} />
          <Stat label="PageRank" value={selected.pagerank != null ? selected.pagerank.toFixed(4) : null} mono />
        </Section>
      )}

      {/* Transaction stats */}
      {!isWallet && (
        <Section title="Transaction">
          <Stat label="Amount" value={selected.amount != null ? `$${Number(selected.amount).toLocaleString()}` : null} />
        </Section>
      )}

      {/* Cluster */}
      {isWallet && walletCluster && (
        <Section title="Cluster Detection">
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
            <p className="text-xs text-yellow-400 font-semibold mb-1">⚠ Part of suspected fraud ring</p>
            <p className="text-xs text-white/50">
              Cluster #{walletCluster.cluster_id} — {walletCluster.size} wallets
            </p>
          </div>
        </Section>
      )}

      {/* Cycles */}
      {isWallet && selected.cycles?.length > 0 && (
        <Section title={`Circular Flows (${selected.cycles.length})`}>
          <div className="space-y-2">
            {selected.cycles.slice(0, 3).map((cycle, i) => (
              <div key={i} className="bg-red-500/10 border border-red-500/20 rounded p-2">
                <p className="text-xs font-mono text-red-400 break-all leading-relaxed">
                  {cycle.join(' → ')}
                </p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* AI Investigation button */}
      {isWallet && (
        <Section title="AI Investigation">
          {!report && !reportLoading && (
            <button
              onClick={() => onInvestigate(selected.id)}
              className="w-full py-2.5 bg-accent/20 hover:bg-accent/30 border border-accent/40 text-accent text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
            >
              <span>✦</span> Generate Investigation Report
            </button>
          )}

          {reportLoading && (
            <div className="flex items-center gap-3 py-3">
              <svg className="animate-spin w-4 h-4 text-accent flex-shrink-0" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeDasharray="32" strokeDashoffset="12"/>
              </svg>
              <span className="text-xs text-white/50">AI agent is investigating…</span>
            </div>
          )}

          {report && !report.error && (
            <div className="space-y-3">
              <div className="bg-accent/10 border border-accent/20 rounded-lg p-3">
                <p className="text-xs leading-relaxed text-white/70 whitespace-pre-wrap">{report.report}</p>
              </div>
              <button
                onClick={() => onInvestigate(selected.id)}
                className="text-xs text-white/30 hover:text-white/60 transition-colors"
              >
                Regenerate ↺
              </button>
            </div>
          )}

          {report?.error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              <p className="text-xs text-red-400">{report.error}</p>
            </div>
          )}
        </Section>
      )}
    </div>
  )
}
