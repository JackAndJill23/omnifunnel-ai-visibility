import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Answer {
  answer_id: number
  raw_text: string
  citations: string[]
  engine: string
  confidence?: number
  answer_hash: string
  created_at: string
}

interface Citation {
  citation_id: number
  url: string
  normalized_domain: string
  position: number
}

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

export default function Dashboard() {
  const [sites, setSites] = useState<Site[]>([])
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null)
  const [answers, setAnswers] = useState<Answer[]>([])
  const [selectedAnswer, setSelectedAnswer] = useState<Answer | null>(null)
  const [citations, setCitations] = useState<Citation[]>([])
  const [selectedEngine, setSelectedEngine] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadSites()
  }, [])

  useEffect(() => {
    if (selectedSite) {
      loadClusters(selectedSite.site_id)
    }
  }, [selectedSite])

  useEffect(() => {
    if (selectedCluster) {
      loadAnswers(selectedCluster.cluster_id, selectedEngine)
    }
  }, [selectedCluster, selectedEngine])

  useEffect(() => {
    if (selectedAnswer) {
      loadCitations(selectedAnswer.answer_id)
    }
  }, [selectedAnswer])

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
        if (data.length > 0) setSelectedCluster(data[0])
      }
    } catch (error) {
      console.error('Failed to load clusters:', error)
    }
  }

  const loadAnswers = async (clusterId: number, engine?: string) => {
    setLoading(true)
    try {
      const engineParam = engine ? `&engine=${engine}` : ''
      const response = await fetch(`http://localhost:8001/v1/clusters/${clusterId}/answers?limit=50${engineParam}`)
      if (response.ok) {
        const data = await response.json()
        setAnswers(data)
      }
    } catch (error) {
      console.error('Failed to load answers:', error)
    }
    setLoading(false)
  }

  const loadCitations = async (answerId: number) => {
    try {
      const response = await fetch(`http://localhost:8001/v1/answers/${answerId}/citations`)
      if (response.ok) {
        const data = await response.json()
        setCitations(data)
      }
    } catch (error) {
      console.error('Failed to load citations:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getEngineColor = (engine: string) => {
    const colors: Record<string, string> = {
      chatgpt: 'bg-green-100 text-green-800',
      claude: 'bg-purple-100 text-purple-800',
      gemini: 'bg-blue-100 text-blue-800',
      perplexity: 'bg-orange-100 text-orange-800',
      bing_copilot: 'bg-cyan-100 text-cyan-800'
    }
    return colors[engine] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← Back to Home</Link>
              <h1 className="text-2xl font-bold text-gray-900 mt-2">AI Visibility Dashboard</h1>
            </div>
            <Link href="/tracking" className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
              Start New Tracking
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Site & Cluster Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Site</label>
            <select
              value={selectedSite?.site_id || ''}
              onChange={(e) => {
                const site = sites.find(s => s.site_id === parseInt(e.target.value))
                setSelectedSite(site || null)
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
            <label className="block text-sm font-medium text-gray-700 mb-2">Cluster</label>
            <select
              value={selectedCluster?.cluster_id || ''}
              onChange={(e) => {
                const cluster = clusters.find(c => c.cluster_id === parseInt(e.target.value))
                setSelectedCluster(cluster || null)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              disabled={!selectedSite}
            >
              <option value="">Select Cluster</option>
              {clusters.map(cluster => (
                <option key={cluster.cluster_id} value={cluster.cluster_id}>{cluster.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Engine Filter</label>
            <select
              value={selectedEngine}
              onChange={(e) => setSelectedEngine(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">All Engines</option>
              <option value="chatgpt">ChatGPT</option>
              <option value="claude">Claude</option>
              <option value="gemini">Gemini</option>
              <option value="perplexity">Perplexity</option>
              <option value="bing_copilot">Bing Copilot</option>
            </select>
          </div>
        </div>

        {!selectedCluster && (
          <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a cluster to view results</h3>
            <p className="text-gray-500 mb-4">Choose a site and cluster from the dropdowns above to see AI visibility data.</p>
            <Link href="/tracking" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
              Create your first cluster →
            </Link>
          </div>
        )}

        {selectedCluster && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Answers List */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Recent Answers
                  {loading && <span className="text-sm text-gray-500 ml-2">(loading...)</span>}
                </h2>
                <div className="text-sm text-gray-500">
                  {answers.length} answers
                </div>
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {answers.map((answer) => (
                  <div
                    key={answer.answer_id}
                    onClick={() => setSelectedAnswer(answer)}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedAnswer?.answer_id === answer.answer_id
                        ? 'border-blue-300 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getEngineColor(answer.engine)}`}>
                        {answer.engine}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(answer.created_at)}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-700 line-clamp-3">
                      {answer.raw_text.length > 150 
                        ? `${answer.raw_text.substring(0, 150)}...`
                        : answer.raw_text
                      }
                    </p>
                    
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-xs text-gray-500">
                        {answer.citations.length} citations
                      </span>
                      <span className="text-xs text-gray-400">
                        #{answer.answer_id}
                      </span>
                    </div>
                  </div>
                ))}
                
                {answers.length === 0 && !loading && (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No answers found for this cluster.</p>
                    <Link href="/tracking" className="text-blue-600 hover:text-blue-800 text-sm mt-2 inline-block">
                      Run your first tracking →
                    </Link>
                  </div>
                )}
              </div>
            </div>

            {/* Answer Details */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Answer Details</h2>
              
              {!selectedAnswer && (
                <p className="text-gray-500">Select an answer to view details and citations.</p>
              )}

              {selectedAnswer && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getEngineColor(selectedAnswer.engine)}`}>
                      {selectedAnswer.engine}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatDate(selectedAnswer.created_at)}
                    </span>
                  </div>

                  <div className="prose prose-sm max-w-none">
                    <div className="bg-gray-50 p-4 rounded-md">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Full Response:</h4>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {selectedAnswer.raw_text}
                      </p>
                    </div>
                  </div>

                  {citations.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-3">
                        Citations ({citations.length})
                      </h4>
                      <div className="space-y-2">
                        {citations.map((citation) => (
                          <div key={citation.citation_id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-md">
                            <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium">
                              {citation.position}
                            </div>
                            <div className="flex-1 min-w-0">
                              <a
                                href={citation.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:text-blue-800 break-all"
                              >
                                {citation.url}
                              </a>
                              <div className="text-xs text-gray-500 mt-1">
                                {citation.normalized_domain}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Answer ID:</span>
                        <div className="font-mono">{selectedAnswer.answer_id}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Hash:</span>
                        <div className="font-mono text-xs">{selectedAnswer.answer_hash.substring(0, 8)}...</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

          </div>
        )}
      </div>
    </div>
  )
}