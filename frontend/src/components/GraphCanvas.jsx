import { useEffect, useRef, useCallback } from 'react'
import cytoscape from 'cytoscape'

const riskColor = (score, flagged) => {
  if (flagged || score >= 80) return '#ef4444'
  if (score >= 60)             return '#f97316'
  if (score >= 35)             return '#eab308'
  return '#22c55e'
}

const CLUSTER_PALETTE = ['#7c6ff7','#06b6d4','#f59e0b','#ec4899','#10b981','#f97316']

function buildStyle(animate) {
  return [
    {
      selector: 'node[type = "wallet"]',
      style: {
        'background-color':   'data(color)',
        'border-width':       2,
        'border-color':       'data(borderColor)',
        'width':              'data(size)',
        'height':             'data(size)',
        'label':              'data(shortId)',
        'color':              '#e2e8f0',
        'font-size':          9,
        'font-family':        'monospace',
        'text-valign':        'bottom',
        'text-margin-y':      4,
        'text-outline-width': 2,
        'text-outline-color': '#0d0f14',
      },
    },
    {
      selector: 'node[type = "transaction"]',
      style: {
        'background-color': '#334155',
        'border-width':     1,
        'border-color':     '#475569',
        'width':            10,
        'height':           10,
        'label':            '',
        'shape':            'diamond',
      },
    },
    {
      selector: 'node.searched',
      style: { 'border-width': 4, 'border-color': '#ffffff', 'width': 52, 'height': 52 },
    },
    {
      selector: 'node.highlighted',
      style: { 'border-width': 3, 'border-color': '#7c6ff7' },
    },
    {
      selector: 'edge',
      style: {
        'width':               1.5,
        'line-color':          '#334155',
        'target-arrow-color':  '#334155',
        'target-arrow-shape':  'triangle',
        'curve-style':         'bezier',
        'opacity':             0.6,
        ...(animate ? {
          'line-dash-pattern': [6, 3],
          'line-dash-offset':  0,
        } : {}),
      },
    },
    {
      selector: 'edge.suspicious',
      style: {
        'line-color':         '#ef4444',
        'target-arrow-color': '#ef4444',
        'width': 2, 'opacity': 0.85,
      },
    },
    {
      selector: 'edge.path-edge',
      style: {
        'line-color':         '#f97316',
        'target-arrow-color': '#f97316',
        'width': 3, 'opacity': 1,
        'z-index': 10,
      },
    },
  ]
}

export default function GraphCanvas({ graphData, searchedAddress, clusters, pathData, animate, onNodeClick }) {
  const containerRef = useRef(null)
  const cyRef        = useRef(null)
  const animFrameRef = useRef(null)

  const clusterMap = useCallback(() => {
    const map = {}
    clusters?.forEach((c, i) => c.wallets.forEach(w => { map[w] = CLUSTER_PALETTE[i % CLUSTER_PALETTE.length] }))
    return map
  }, [clusters])

  // Init Cytoscape once
  useEffect(() => {
    if (!containerRef.current) return
    cyRef.current = cytoscape({
      container: containerRef.current,
      style: buildStyle(animate),
      elements: [],
      userZoomingEnabled: true,
      userPanningEnabled: true,
      minZoom: 0.15,
      maxZoom: 5,
    })
    return () => {
      cancelAnimationFrame(animFrameRef.current)
      cyRef.current?.destroy()
    }
  }, []) // eslint-disable-line

  // Animate edges with dash offset
  useEffect(() => {
    cancelAnimationFrame(animFrameRef.current)
    if (!animate || !cyRef.current) return
    let offset = 0
    const tick = () => {
      offset = (offset - 1) % 60
      cyRef.current?.edges().not('.path-edge').style('line-dash-offset', offset)
      animFrameRef.current = requestAnimationFrame(tick)
    }
    animFrameRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(animFrameRef.current)
  }, [animate, graphData])

  // Rebuild graph when data changes
  useEffect(() => {
    const cy = cyRef.current
    if (!cy || !graphData) return

    cy.elements().remove()
    const cMap = clusterMap()
    const elements = []

    graphData.nodes.forEach(n => {
      if (n.type === 'wallet') {
        const color = cMap[n.id] || riskColor(n.risk_score, n.flagged)
        elements.push({
          data: {
            id: n.id, type: 'wallet',
            risk_score: n.risk_score, flagged: n.flagged,
            color: color + 'cc', borderColor: color,
            size: n.id === searchedAddress ? 52 : (n.flagged ? 36 : 26),
            shortId: n.id.slice(0, 10) + '…',
          },
          classes: n.id === searchedAddress ? 'searched' : '',
        })
      } else {
        elements.push({ data: { id: n.id, type: 'transaction', amount: n.amount } })
      }
    })

    const nodeIds = new Set(graphData.nodes.map(n => n.id))
graphData.edges.forEach((e, i) => {
  if (!nodeIds.has(e.source) || !nodeIds.has(e.target)) return
  const srcFlagged = graphData.nodes.find(n => n.id === e.source)?.flagged
  elements.push({
    data: { id: `e${i}`, source: e.source, target: e.target },
    classes: srcFlagged ? 'suspicious' : '',
  })
})

    cy.add(elements)
    cy.style(buildStyle(animate))

    cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 800,
      randomize: false,
      nodeRepulsion: 9000,
      idealEdgeLength: 90,
      fit: true,
      padding: 50,
    }).run()

    // Click handlers
    cy.removeAllListeners()
    cy.on('tap', 'node', evt => {
      cy.nodes().removeClass('highlighted')
      evt.target.addClass('highlighted')
      const d = evt.target.data()
      onNodeClick({ id: d.id, type: d.type, risk_score: d.risk_score, flagged: d.flagged })
    })
    cy.on('tap', evt => {
      if (evt.target === cy) {
        cy.nodes().removeClass('highlighted')
        onNodeClick(null)
      }
    })
  }, [graphData, clusters, searchedAddress, animate, clusterMap, onNodeClick])

  // Highlight path when pathData changes
  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return
    cy.edges().removeClass('path-edge')
    if (!pathData?.path?.length) return
    pathData.path.forEach((addr, i) => {
      if (i < pathData.path.length - 1) {
        const next = pathData.path[i + 1]
        cy.edges().filter(e =>
          (e.data('source') === addr && e.data('target') === next) ||
          (e.data('source') === next && e.data('target') === addr)
        ).addClass('path-edge')
      }
    })
  }, [pathData])

  return (
    <div className="relative w-full h-full">
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  )
}
