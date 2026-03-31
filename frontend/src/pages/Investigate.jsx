import { useCallback, useState } from 'react'
import GraphCanvas    from '../components/GraphCanvas'
import Sidebar        from '../components/Sidebar'
import SearchBar      from '../components/SearchBar'
import PathTracer     from '../components/PathTracer'
import ClustersPanel  from '../components/ClustersPanel'
import PageRankPanel  from '../components/PageRankPanel'
import { useGraph }   from '../hooks/useGraph'

const TABS = [
  { id: 'inspect',  label: 'Inspect' },
  { id: 'path',     label: 'Path tracer' },
  { id: 'clusters', label: 'Clusters' },
  { id: 'pagerank', label: 'PageRank' },
]

export default function Investigate() {
  const {
    graphData, selected, report, clusters,
    loading, reportLoading, error, searchedAddress,
    search, selectNode, investigate,
  } = useGraph()

  const [tab, setTab]         = useState('inspect')
  const [hops, setHops]       = useState(2)
  const [pathData, setPathData] = useState(null)
  const [animate, setAnimate] = useState(true)

  const handleSearch = useCallback((addr) => {
    search(addr, hops)
    setTab('inspect')
    setPathData(null)
  }, [search, hops])

  const handleNodeClick = useCallback((node) => {
    if (node) {
      selectNode(node)
      setTab('inspect')
    }
  }, [selectNode])

  const handleSelectWallet = useCallback((addr) => {
    search(addr, hops)
    setTab('inspect')
  }, [search, hops])

  return (
    <div className="flex flex-col h-screen bg-bg">

      {/* ── Top bar ── */}
      <header className="flex items-center gap-3 px-4 py-2.5 border-b border-border bg-surface flex-shrink-0">
        {/* Logo */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-7 h-7 rounded bg-accent/20 border border-accent/30 flex items-center justify-center text-accent text-sm">⬡</div>
          <span className="font-bold text-white text-sm tracking-tight hidden sm:block">ChainTrace AI</span>
        </div>

        {/* Search */}
        <SearchBar onSearch={handleSearch} loading={loading} />

        {/* Hops slider */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-white/30 hidden md:block">Hops</span>
          <input
            type="range" min={1} max={4} value={hops}
            onChange={e => setHops(Number(e.target.value))}
            className="w-16 accent-accent"
          />
          <span className="text-xs font-mono text-white/50 w-3">{hops}</span>
        </div>

        {/* Animate toggle */}
        <button
          onClick={() => setAnimate(a => !a)}
          className={`flex-shrink-0 text-xs px-2.5 py-1 rounded border transition-all ${
            animate
              ? 'bg-accent/20 border-accent/40 text-accent'
              : 'bg-white/5 border-white/10 text-white/30'
          }`}
        >
          {animate ? '⚡ Live' : '⏸ Static'}
        </button>

        {/* Stats */}
        {graphData && (
          <div className="ml-auto flex items-center gap-2 flex-shrink-0 text-xs text-white/30">
            <span>{graphData.nodes.filter(n => n.type === 'wallet').length}W</span>
            <span className="text-white/10">·</span>
            <span>{graphData.edges.length}E</span>
            {clusters.length > 0 && (
              <><span className="text-white/10">·</span>
              <span className="text-yellow-400">{clusters.length} rings</span></>
            )}
          </div>
        )}
      </header>

      {/* ── Error banner ── */}
      {error && (
        <div className="bg-red-500/10 border-b border-red-500/20 px-4 py-1.5 text-xs text-red-400 flex-shrink-0">
          {error}
        </div>
      )}

      {/* ── Main layout ── */}
      <div className="flex flex-1 min-h-0">

        {/* Graph canvas */}
        <div className="flex-1 min-w-0 relative">
          <GraphCanvas
            graphData={graphData}
            searchedAddress={searchedAddress}
            clusters={clusters}
            pathData={pathData}
            animate={animate}
            onNodeClick={handleNodeClick}
          />

          {/* Legend */}
          {graphData && (
            <div className="absolute bottom-4 left-4 bg-surface/90 backdrop-blur border border-border rounded-lg px-3 py-2 flex items-center gap-3 flex-wrap">
              {[
                ['bg-red-500',    'Critical ≥80'],
                ['bg-orange-500', 'High ≥60'],
                ['bg-yellow-500', 'Medium ≥35'],
                ['bg-green-500',  'Low'],
              ].map(([color, label]) => (
                <div key={label} className="flex items-center gap-1.5">
                  <div className={`w-2 h-2 rounded-full ${color}`} />
                  <span className="text-xs text-white/40">{label}</span>
                </div>
              ))}
              <div className="w-px h-3 bg-white/10" />
              <div className="flex items-center gap-1.5">
                <div className="w-4 h-px bg-orange-500" />
                <span className="text-xs text-white/40">Path</span>
              </div>
            </div>
          )}

          {/* Empty state */}
          {!graphData && !loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-white/15 select-none pointer-events-none">
              <div className="text-5xl mb-3">⬡</div>
              <p className="text-sm">Enter a wallet address to begin</p>
              <p className="text-xs mt-1">Try: 0xENTRY0001</p>
            </div>
          )}
        </div>

        {/* ── Right panel ── */}
        <aside className="w-80 flex-shrink-0 border-l border-border bg-panel flex flex-col">

          {/* Tabs */}
          <div className="flex border-b border-border flex-shrink-0">
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`flex-1 text-xs py-2.5 transition-colors border-b-2 ${
                  tab === t.id
                    ? 'border-accent text-accent'
                    : 'border-transparent text-white/30 hover:text-white/60'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-y-auto p-4">
            {tab === 'inspect' && (
              <Sidebar
                selected={selected}
                report={report}
                reportLoading={reportLoading}
                onInvestigate={investigate}
                clusters={clusters}
              />
            )}
            {tab === 'path' && (
              <PathTracer onPathFound={setPathData} />
            )}
            {tab === 'clusters' && (
              <ClustersPanel clusters={clusters} onSelectWallet={handleSelectWallet} />
            )}
            {tab === 'pagerank' && (
              <PageRankPanel onSelectWallet={handleSelectWallet} />
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
