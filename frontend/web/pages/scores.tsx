import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Site {
  site_id: number
  domain: string
  cms_type?: string
  created_at: string
}

interface Cluster {
  cluster_id: number
  name: string
  description?: string
  keywords: string[]
  created_at: string
}

interface ScoreData {
  site_id: number
  cluster_id?: number
  total: number
  subscores: {
    prompt_sov: number
    generative_appearance: number
    citation_authority: number
    answer_quality: number
    voice_presence: number
    ai_traffic: number
    ai_conversions: number
  }
  calculated_at: string
  engine_breakdown: Record<string, number>
  recommendations: string[]
}

interface ScoreHistory {
  score_id: number
  total: number
  subscores: Record<string, number>
  calculated_at: string
}

export default function Scores() {
  const [sites, setSites] = useState<Site[]>([])
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null)
  const [currentScore, setCurrentScore] = useState<ScoreData | null>(null)
  const [scoreHistory, setScoreHistory] = useState<ScoreHistory[]>([])
  const [loading, setLoading] = useState(false)
  const [calculating, setCalculating] = useState(false)

  useEffect(() => {
    loadSites()
  }, [])

  useEffect(() => {
    if (selectedSite) {
      loadClusters(selectedSite.site_id)
    }
  }, [selectedSite])

  useEffect(() => {
    if (selectedSite) {
      loadCurrentScore()
      loadScoreHistory()
    }
  }, [selectedSite, selectedCluster])

  const loadSites = async () => {
    try {
      const response = await fetch(`http://localhost:8001/v1/sites?tenant_id=1`)
      if (response.ok) {
        const data = await response.json()
        setSites(data)
        if (data.length > 0) setSelectedSite(data[0])
      }
    } catch (error) {
      console.error('Failed to load sites:', error)
    }
  }

  const loadClusters = async (siteId: number) => {
    try {
      const response = await fetch(`http://localhost:8001/v1/sites/${siteId}/clusters`)
      if (response.ok) {
        const data = await response.json()
        setClusters(data)
      }
    } catch (error) {
      console.error('Failed to load clusters:', error)
    }
  }

  const loadCurrentScore = async () => {
    if (!selectedSite) return

    setLoading(true)
    try {
      const clusterParam = selectedCluster ? `&cluster_id=${selectedCluster.cluster_id}` : ''
      const response = await fetch(`http://localhost:8004/v1/score?site_id=${selectedSite.site_id}${clusterParam}`)
      if (response.ok) {
        const data = await response.json()
        setCurrentScore(data)
      } else if (response.status === 404) {
        setCurrentScore(null)
      }
    } catch (error) {
      console.error('Failed to load current score:', error)
      setCurrentScore(null)
    }
    setLoading(false)
  }

  const loadScoreHistory = async () => {
    if (!selectedSite) return

    try {
      const clusterParam = selectedCluster ? `&cluster_id=${selectedCluster.cluster_id}` : ''
      const response = await fetch(`http://localhost:8004/v1/score-history?site_id=${selectedSite.site_id}${clusterParam}&days=30`)
      if (response.ok) {
        const data = await response.json()
        setScoreHistory(data)
      }
    } catch (error) {
      console.error('Failed to load score history:', error)
    }
  }

  const calculateNewScore = async () => {
    if (!selectedSite) return

    setCalculating(true)
    try {
      const response = await fetch('http://localhost:8004/v1/calculate-score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_id: selectedSite.site_id,
          cluster_id: selectedCluster?.cluster_id,
          date_range_days: 30
        })
      })
      
      if (response.ok) {
        const newScore = await response.json()
        setCurrentScore(newScore)
        loadScoreHistory() // Refresh history
      }
    } catch (error) {
      console.error('Failed to calculate score:', error)
    }
    setCalculating(false)
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    if (score >= 40) return 'text-orange-600 bg-orange-100'
    return 'text-red-600 bg-red-100'
  }

  const getScoreGrade = (score: number) => {
    if (score >= 90) return 'A+'
    if (score >= 80) return 'A'
    if (score >= 70) return 'B'
    if (score >= 60) return 'C'
    if (score >= 50) return 'D'
    return 'F'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← Back to Home</Link>
              <h1 className="text-2xl font-bold text-gray-900 mt-2">AI Visibility Score™</h1>
              <p className="text-sm text-gray-500">Track your brand's performance across AI engines</p>
            </div>
            <div className="flex space-x-4">
              <Link href="/dashboard" className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200">
                View Data
              </Link>
              <button
                onClick={calculateNewScore}
                disabled={calculating || !selectedSite}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {calculating ? 'Calculating...' : 'Calculate Score'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Site & Cluster Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Site</label>
            <select
              value={selectedSite?.site_id || ''}
              onChange={(e) => {
                const site = sites.find(s => s.site_id === parseInt(e.target.value))
                setSelectedSite(site || null)
                setSelectedCluster(null)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">Select Site</option>
              {sites.map(site => (
                <option key={site.site_id} value={site.site_id}>{site.domain}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Cluster (Optional)</label>
            <select
              value={selectedCluster?.cluster_id || ''}
              onChange={(e) => {
                const cluster = clusters.find(c => c.cluster_id === parseInt(e.target.value))
                setSelectedCluster(cluster || null)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              disabled={!selectedSite}
            >
              <option value="">All Clusters</option>
              {clusters.map(cluster => (
                <option key={cluster.cluster_id} value={cluster.cluster_id}>{cluster.name}</option>
              ))}
            </select>
          </div>
        </div>

        {!selectedSite && (
          <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a site to view AI Visibility Score</h3>
            <p className="text-gray-500 mb-4">Choose a site from the dropdown above to see performance metrics.</p>
          </div>
        )}

        {selectedSite && !currentScore && !loading && (
          <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No score calculated yet</h3>
            <p className="text-gray-500 mb-4">Calculate your first AI Visibility Score to see performance metrics.</p>
            <button
              onClick={calculateNewScore}
              disabled={calculating}
              className="bg-blue-600 text-white px-6 py-3 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {calculating ? 'Calculating...' : 'Calculate AI Visibility Score'}
            </button>
          </div>
        )}

        {loading && (
          <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
            <p className="text-gray-500">Loading score data...</p>
          </div>
        )}

        {currentScore && (
          <div className="space-y-8">
            
            {/* Overall Score */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Overall AI Visibility Score</h2>
                <div className="text-xs text-gray-500">
                  Last calculated: {formatDate(currentScore.calculated_at)}
                </div>
              </div>

              <div className="flex items-center space-x-8">
                <div className="text-center">
                  <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full text-3xl font-bold ${getScoreColor(currentScore.total)}`}>
                    {Math.round(currentScore.total)}
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    Grade: {getScoreGrade(currentScore.total)}
                  </div>
                </div>
                
                <div className="flex-1">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Performance Level</span>
                      <span className="text-sm font-medium">
                        {currentScore.total >= 80 ? 'Excellent' : 
                         currentScore.total >= 60 ? 'Good' : 
                         currentScore.total >= 40 ? 'Fair' : 'Needs Improvement'}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          currentScore.total >= 80 ? 'bg-green-500' : 
                          currentScore.total >= 60 ? 'bg-yellow-500' : 
                          currentScore.total >= 40 ? 'bg-orange-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(currentScore.total, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              
              {/* Component Scores */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Components</h3>
                <div className="space-y-4">
                  {[
                    { key: 'prompt_sov', label: 'Prompt Share of Voice', weight: '30%' },
                    { key: 'generative_appearance', label: 'Generative Appearance Rate', weight: '20%' },
                    { key: 'citation_authority', label: 'Citation Authority Mix', weight: '15%' },
                    { key: 'answer_quality', label: 'Answer Quality Proxy', weight: '10%' },
                    { key: 'ai_traffic', label: 'AI Traffic Attribution', weight: '10%' },
                    { key: 'ai_conversions', label: 'AI Conversions', weight: '10%' },
                    { key: 'voice_presence', label: 'Voice Presence', weight: '5%' },
                  ].map(({ key, label, weight }) => (
                    <div key={key} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">{label}</span>
                          <span className="text-xs text-gray-500">{weight}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${Math.min(currentScore.subscores[key] || 0, 100)}%` }}
                          />
                        </div>
                      </div>
                      <div className="ml-4 text-sm font-medium text-gray-900 w-12 text-right">
                        {Math.round(currentScore.subscores[key] || 0)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Engine Breakdown */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Engine Performance</h3>
                {Object.keys(currentScore.engine_breakdown).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(currentScore.engine_breakdown).map(([engine, score]) => (
                      <div key={engine} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 capitalize">{engine}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${Math.min(score, 100)}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-900 w-8 text-right">
                            {Math.round(score)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No engine data available yet.</p>
                )}
              </div>

              {/* Recommendations */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
                {currentScore.recommendations.length > 0 ? (
                  <ul className="space-y-3">
                    {currentScore.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium mt-0.5">
                          {index + 1}
                        </div>
                        <span className="text-sm text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm">No recommendations available.</p>
                )}
              </div>

              {/* Score History */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Score History</h3>
                {scoreHistory.length > 0 ? (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {scoreHistory.map((score) => (
                      <div key={score.score_id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                        <span className="text-sm text-gray-600">
                          {formatDate(score.calculated_at)}
                        </span>
                        <div className="flex items-center space-x-2">
                          <div className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(score.total)}`}>
                            {Math.round(score.total)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No historical data available yet.</p>
                )}
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  )
}