import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
})

export const fetchWalletNetwork = (address, hops = 2) =>
  api.get(`/api/graph/wallet/${address}?hops=${hops}`).then(r => r.data)

export const fetchWalletDetails = (address) =>
  api.get(`/api/graph/wallet/${address}/details`).then(r => r.data)

export const fetchShortestPath = (source, target) =>
  api.get(`/api/graph/path?source=${source}&target=${target}`).then(r => r.data)

export const fetchClusters = () =>
  api.get('/api/analysis/clusters').then(r => r.data)

export const fetchPageRank = () =>
  api.get('/api/analysis/pagerank').then(r => r.data)

export const fetchCycles = (address) =>
  api.get(`/api/analysis/cycles/${address}`).then(r => r.data)

export const fetchFullAnalysis = (address) =>
  api.get(`/api/analysis/wallet/${address}/full`).then(r => r.data)

export const generateReport = (wallet_address) =>
  api.post('/api/ai/investigate', { wallet_address }).then(r => r.data)
