import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Site {
  site_id: number
  domain: string
}

interface Cluster {
  cluster_id: number
  name: string
}

interface CompetitorData {
  mentions: number
  citations: number
  engines: string[]
  presence_score: number
}

interface CompetitiveAnalysis {
  site_id: number
  cluster_id: number
  analysis_date: string
  competitors: Record<string, CompetitorData>
  recommendation: string[]
}

interface EntityMapping {
  entity_id: number
  brand_name: string
  same_as_links: Array<{url: string, platform: string, status: string}>
  wikidata_id: string
}

export default function Intelligence() {
  const [sites, setSites] = useState<Site[]>([])
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null)
  
  // Competitive Analysis
  const [competitors, setCompetitors] = useState<string[]>([''])
  const [competitiveAnalysis, setCompetitiveAnalysis] = useState<CompetitiveAnalysis | null>(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  
  // Entity Stitching
  const [brandName, setBrandName] = useState('')
  const [entityMappings, setEntityMappings] = useState<EntityMapping[]>([])
  const [entityLoading, setEntityLoading] = useState(false)

  useEffect(() => {
    loadSites()
  }, [])

  useEffect(() => {
    if (selectedSite) {
      loadClusters(selectedSite.site_id)
      loadEntityMappings(selectedSite.site_id)
    }
  }, [selectedSite])

  const loadSites = async () => {
    try {
      const response = await fetch('http://localhost:8001/v1/sites?tenant_id=1')
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

  const loadEntityMappings = async (siteId: number) => {
    try {
      const response = await fetch(`http://localhost:8003/v1/entity/mappings?site_id=${siteId}`)
      if (response.ok) {
        const data = await response.json()
        setEntityMappings(data)
      }
    } catch (error) {
      console.error('Failed to load entity mappings:', error)
    }
  }

  const runCompetitiveAnalysis = async () => {
    if (!selectedSite || !selectedCluster) return

    setAnalysisLoading(true)
    try {
      const validCompetitors = competitors.filter(c => c.trim() !== '')
      
      const response = await fetch('http://localhost:8003/v1/competitive/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_id: selectedSite.site_id,
          cluster_id: selectedCluster.cluster_id,
          competitors: validCompetitors,
          time_range_days: 30
        })
      })

      if (response.ok) {
        const data = await response.json()
        setCompetitiveAnalysis(data)
      }
    } catch (error) {
      console.error('Competitive analysis error:', error)
    }
    setAnalysisLoading(false)
  }

  const generateEntityStitching = async () => {
    if (!selectedSite || !brandName.trim()) return

    setEntityLoading(true)
    try {
      const response = await fetch('http://localhost:8003/v1/entity/stitch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_id: selectedSite.site_id,
          brand_name: brandName,
          entity_type: 'brand'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setEntityMappings([...entityMappings, data])
        setBrandName('')
      }
    } catch (error) {
      console.error('Entity stitching error:', error)
    }
    setEntityLoading(false)
  }

  const addCompetitor = () => {
    setCompetitors([...competitors, ''])
  }

  const updateCompetitor = (index: number, value: string) => {
    const updated = [...competitors]
    updated[index] = value
    setCompetitors(updated)
  }

  const removeCompetitor = (index: number) => {
    setCompetitors(competitors.filter((_, i) => i !== index))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← Back to Home</Link>
              <h1 className="text-2xl font-bold text-gray-900 mt-2">Competitive Intelligence & Entity Analysis</h1>
              <p className="text-sm text-gray-500">Track competitors and optimize entity connections</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Site Selection */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Site</label>
              <select
                value={selectedSite?.site_id || ''}
                onChange={(e) => {
                  const site = sites.find(s => s.site_id === parseInt(e.target.value))
                  setSelectedSite(site || null)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                disabled={!selectedSite}
              >
                <option value="">Select Cluster</option>
                {clusters.map(cluster => (
                  <option key={cluster.cluster_id} value={cluster.cluster_id}>{cluster.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Competitive Analysis */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Competitive Analysis</h2>
            
            <div className="space-y-3 mb-4">
              <label className="block text-sm font-medium text-gray-700">Competitor Domains</label>
              {competitors.map((competitor, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={competitor}
                    onChange={(e) => updateCompetitor(index, e.target.value)}
                    placeholder="competitor.com"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                  {competitors.length > 1 && (
                    <button
                      onClick={() => removeCompetitor(index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={addCompetitor}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                + Add Competitor
              </button>
            </div>

            <button
              onClick={runCompetitiveAnalysis}
              disabled={analysisLoading || !selectedCluster || competitors.filter(c => c.trim()).length === 0}
              className="w-full bg-purple-600 text-white py-3 rounded-md font-medium hover:bg-purple-700 disabled:opacity-50"
            >
              {analysisLoading ? 'Analyzing...' : 'Run Competitive Analysis'}
            </button>

            {/* Competitive Analysis Results */}
            {competitiveAnalysis && (
              <div className="mt-6 space-y-4">
                <h3 className="font-semibold text-gray-900">Analysis Results</h3>
                
                {Object.entries(competitiveAnalysis.competitors).map(([competitor, data]) => (
                  <div key={competitor} className="border border-gray-200 rounded-md p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">{competitor}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        data.presence_score >= 70 ? 'bg-red-100 text-red-800' :
                        data.presence_score >= 40 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {data.presence_score} score
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 grid grid-cols-3 gap-2">
                      <div>Mentions: {data.mentions}</div>
                      <div>Citations: {data.citations}</div>
                      <div>Engines: {data.engines.length}</div>
                    </div>
                  </div>
                ))}

                {competitiveAnalysis.recommendation.length > 0 && (
                  <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                    <h4 className="font-semibold text-blue-900 mb-2">Recommendations</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      {competitiveAnalysis.recommendation.map((rec, i) => (
                        <li key={i}>• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Entity Stitching */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Entity Stitching & SameAs Links</h2>
            
            <div className="space-y-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Brand Name</label>
                <input
                  type="text"
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                  placeholder="Your Brand Name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>

              <button
                onClick={generateEntityStitching}
                disabled={entityLoading || !selectedSite || !brandName.trim()}
                className="w-full bg-indigo-600 text-white py-3 rounded-md font-medium hover:bg-indigo-700 disabled:opacity-50"
              >
                {entityLoading ? 'Generating...' : 'Generate SameAs Links'}
              </button>
            </div>

            {/* Entity Mappings */}
            {entityMappings.length > 0 && (
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Entity Mappings</h3>
                
                {entityMappings.map((entity, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-4">
                    <div className="flex justify-between items-center mb-3">
                      <span className="font-medium text-gray-900">{entity.brand_name}</span>
                      <span className="text-xs text-gray-500">Wikidata: {entity.wikidata_id}</span>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-700">SameAs Links:</h4>
                      {entity.same_as_links.map((link, linkIndex) => (
                        <div key={linkIndex} className="flex items-center justify-between text-xs">
                          <a 
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 truncate flex-1 mr-2"
                          >
                            {link.platform}
                          </a>
                          <span className={`px-2 py-1 rounded ${
                            link.status === 'found' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {link.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* Performance Deltas & Alerts */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Alerts & Changes</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-green-50 border border-green-200 rounded-md p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">Improvement Detected</h3>
                  <p className="text-sm text-green-700 mt-1">Citations in Gemini increased by 60% (8 vs 5)</p>
                </div>
              </div>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Issue Detected</h3>
                  <p className="text-sm text-red-700 mt-1">Presence in Perplexity dropped by 57% (3 vs 7)</p>
                  <button className="text-xs text-red-600 hover:text-red-800 mt-1 font-medium">
                    → Auto-Remediate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}