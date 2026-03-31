import { useState, useCallback } from 'react'
import {
  fetchWalletNetwork,
  fetchWalletDetails,
  fetchCycles,
  fetchClusters,
  generateReport,
} from '../services/api'

export function useGraph() {
  const [graphData, setGraphData]       = useState(null)
  const [selected, setSelected]         = useState(null)
  const [report, setReport]             = useState(null)
  const [clusters, setClusters]         = useState([])
  const [loading, setLoading]           = useState(false)
  const [reportLoading, setReportLoading] = useState(false)
  const [error, setError]               = useState(null)
  const [searchedAddress, setSearchedAddress] = useState(null)

  const search = useCallback(async (address, hops = 2) => {
    setLoading(true)
    setError(null)
    setReport(null)
    setSelected(null)
    setSearchedAddress(address)
    try {
      const [network, clusterData] = await Promise.all([
        fetchWalletNetwork(address, hops),
        fetchClusters(),
      ])
      // Tag nodes that belong to a cluster
      const clusterMap = {}
      clusterData.clusters.forEach(c => {
        c.wallets.forEach(w => { clusterMap[w] = c.cluster_id })
      })
      network.nodes = network.nodes.map(n => ({
        ...n,
        cluster_id: clusterMap[n.id] ?? null,
      }))
      setGraphData(network)
      setClusters(clusterData.clusters)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to load wallet network')
    } finally {
      setLoading(false)
    }
  }, [])

  const selectNode = useCallback(async (node) => {
    if (node.type !== 'wallet') { setSelected(node); return }
    try {
      const [details, cycleData] = await Promise.all([
        fetchWalletDetails(node.id),
        fetchCycles(node.id),
      ])
      setSelected({ ...node, ...details, cycles: cycleData.cycles })
    } catch {
      setSelected(node)
    }
  }, [])

  const investigate = useCallback(async (address) => {
    setReportLoading(true)
    setReport(null)
    try {
      const data = await generateReport(address)
      setReport(data)
    } catch (e) {
      setReport({ error: e.response?.data?.detail || 'AI report failed' })
    } finally {
      setReportLoading(false)
    }
  }, [])

  return {
    graphData, selected, report, clusters,
    loading, reportLoading, error, searchedAddress,
    search, selectNode, investigate,
  }
}
