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

interface Run {
  run_id: number
  status: string
  engine?: string
  started_at: string
  variant_count: number
}

export default function Tracking() {
  const [sites, setSites] = useState<Site[]>([])
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null)
  const [runs, setRuns] = useState<Run[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Form states
  const [newSite, setNewSite] = useState({ domain: '', cms_type: '' })
  const [newCluster, setNewCluster] = useState({ 
    name: '', 
    description: '', 
    seed_prompt: '', 
    keywords: [] as string[]
  })
  const [runRequest, setRunRequest] = useState({
    engine: '',
    variant_sample: 25
  })

  const [showSiteForm, setShowSiteForm] = useState(false)
  const [showClusterForm, setShowClusterForm] = useState(false)

  // Load sites on mount
  useEffect(() => {
    loadSites()
  }, [])

  // Load clusters when site is selected
  useEffect(() => {
    if (selectedSite) {
      loadClusters(selectedSite.site_id)
    }
  }, [selectedSite])

  const loadSites = async () => {
    try {
      const response = await fetch(`http://localhost:8001/v1/sites?tenant_id=1`)
      if (response.ok) {
        const data = await response.json()
        setSites(data)
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

  const createSite = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setLoading(true)
    
    try {
      console.log('Creating site with data:', { ...newSite, tenant_id: 1 })
      
      const response = await fetch('http://localhost:8001/v1/sites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newSite,
          tenant_id: 1
        })
      })
      
      console.log('Site creation response:', response.status, response.ok)
      
      if (response.ok) {
        const responseData = await response.json()
        console.log('Site created successfully:', responseData)
        
        setNewSite({ domain: '', cms_type: '' })
        setShowSiteForm(false)
        setSuccess(`Site "${newSite.domain}" created successfully!`)
        await loadSites()
      } else {
        const errorData = await response.text()
        setError(`Failed to create site: ${response.status} - ${errorData}`)
      }
    } catch (error) {
      console.error('Failed to create site:', error)
      setError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
    setLoading(false)
  }

  const createCluster = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedSite) return
    
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/v1/sites/${selectedSite.site_id}/clusters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCluster)
      })
      if (response.ok) {
        setNewCluster({ name: '', description: '', seed_prompt: '', keywords: [] })
        setShowClusterForm(false)
        loadClusters(selectedSite.site_id)
      }
    } catch (error) {
      console.error('Failed to create cluster:', error)
    }
    setLoading(false)
  }

  const runTracking = async () => {
    if (!selectedCluster) return
    
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/v1/clusters/${selectedCluster.cluster_id}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(runRequest)
      })
      if (response.ok) {
        const run = await response.json()
        setRuns([run, ...runs])
        alert(`Tracking run started! Run ID: ${run.run_id}`)
      }
    } catch (error) {
      console.error('Failed to start tracking run:', error)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← Back to Home</Link>
              <h1 className="text-2xl font-bold text-gray-900 mt-2">AI Visibility Tracking</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
                <button 
                  onClick={() => setError(null)}
                  className="mt-2 text-xs text-red-600 hover:text-red-800"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}
        
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">Success</h3>
                <div className="mt-2 text-sm text-green-700">{success}</div>
                <button 
                  onClick={() => setSuccess(null)}
                  className="mt-2 text-xs text-green-600 hover:text-green-800"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Sites Panel */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Sites</h2>
              <button
                onClick={() => setShowSiteForm(!showSiteForm)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                + Add Site
              </button>
            </div>

            {showSiteForm && (
              <form onSubmit={createSite} className="mb-4 p-4 border rounded-md bg-gray-50">
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Domain (e.g., example.com)"
                    value={newSite.domain}
                    onChange={(e) => setNewSite({...newSite, domain: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md text-sm"
                    required
                  />
                  <select
                    value={newSite.cms_type}
                    onChange={(e) => setNewSite({...newSite, cms_type: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md text-sm"
                  >
                    <option value="">Select CMS (optional)</option>
                    <option value="wordpress">WordPress</option>
                    <option value="webflow">Webflow</option>
                    <option value="shopify">Shopify</option>
                    <option value="hubspot">HubSpot</option>
                  </select>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-2 rounded-md text-sm hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create Site'}
                  </button>
                </div>
              </form>
            )}

            <div className="space-y-2">
              {sites.map((site) => (
                <div
                  key={site.site_id}
                  onClick={() => setSelectedSite(site)}
                  className={`p-3 border rounded-md cursor-pointer transition-colors ${
                    selectedSite?.site_id === site.site_id
                      ? 'border-blue-300 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{site.domain}</div>
                  {site.cms_type && (
                    <div className="text-xs text-gray-500 capitalize">{site.cms_type}</div>
                  )}
                </div>
              ))}
              {sites.length === 0 && (
                <p className="text-gray-500 text-sm">No sites yet. Create one to get started.</p>
              )}
            </div>
          </div>

          {/* Clusters Panel */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Clusters</h2>
              {selectedSite && (
                <button
                  onClick={() => setShowClusterForm(!showClusterForm)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  + Add Cluster
                </button>
              )}
            </div>

            {!selectedSite && (
              <p className="text-gray-500 text-sm">Select a site first to view clusters.</p>
            )}

            {selectedSite && showClusterForm && (
              <form onSubmit={createCluster} className="mb-4 p-4 border rounded-md bg-gray-50">
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Cluster name"
                    value={newCluster.name}
                    onChange={(e) => setNewCluster({...newCluster, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md text-sm"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Description (optional)"
                    value={newCluster.description}
                    onChange={(e) => setNewCluster({...newCluster, description: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md text-sm"
                  />
                  <textarea
                    placeholder="Seed prompt (e.g., 'best AI SEO tools')"
                    value={newCluster.seed_prompt}
                    onChange={(e) => setNewCluster({...newCluster, seed_prompt: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md text-sm"
                    rows={3}
                    required
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-2 rounded-md text-sm hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create Cluster'}
                  </button>
                </div>
              </form>
            )}

            {selectedSite && (
              <div className="space-y-2">
                {clusters.map((cluster) => (
                  <div
                    key={cluster.cluster_id}
                    onClick={() => setSelectedCluster(cluster)}
                    className={`p-3 border rounded-md cursor-pointer transition-colors ${
                      selectedCluster?.cluster_id === cluster.cluster_id
                        ? 'border-green-300 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-sm">{cluster.name}</div>
                    {cluster.description && (
                      <div className="text-xs text-gray-500">{cluster.description}</div>
                    )}
                    <div className="text-xs text-gray-400 mt-1">
                      {cluster.keywords.length} keywords
                    </div>
                  </div>
                ))}
                {clusters.length === 0 && (
                  <p className="text-gray-500 text-sm">No clusters yet. Create one to start tracking.</p>
                )}
              </div>
            )}
          </div>

          {/* Tracking Panel */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Run Tracking</h2>
            
            {!selectedCluster && (
              <p className="text-gray-500 text-sm">Select a cluster to run AI visibility tracking.</p>
            )}

            {selectedCluster && (
              <div className="space-y-4">
                <div className="p-3 bg-gray-50 rounded-md">
                  <div className="text-sm font-medium">Selected Cluster</div>
                  <div className="text-sm text-gray-600">{selectedCluster.name}</div>
                  {selectedCluster.description && (
                    <div className="text-xs text-gray-500">{selectedCluster.description}</div>
                  )}
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Engine (optional)
                    </label>
                    <select
                      value={runRequest.engine}
                      onChange={(e) => setRunRequest({...runRequest, engine: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md text-sm"
                    >
                      <option value="">All Engines</option>
                      <option value="chatgpt">ChatGPT</option>
                      <option value="claude">Claude</option>
                      <option value="gemini">Gemini</option>
                      <option value="perplexity">Perplexity</option>
                      <option value="bing_copilot">Bing Copilot</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Variant Sample Size
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={runRequest.variant_sample}
                      onChange={(e) => setRunRequest({...runRequest, variant_sample: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border rounded-md text-sm"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Number of prompt variants to test (1-100)
                    </div>
                  </div>

                  <button
                    onClick={runTracking}
                    disabled={loading}
                    className="w-full bg-green-600 text-white py-3 rounded-md text-sm font-medium hover:bg-green-700 disabled:opacity-50"
                  >
                    {loading ? 'Starting...' : 'Start AI Tracking Run'}
                  </button>
                </div>

                {runs.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Recent Runs</h3>
                    <div className="space-y-2">
                      {runs.slice(0, 3).map((run) => (
                        <div key={run.run_id} className="p-2 border rounded text-xs">
                          <div className="flex justify-between">
                            <span>Run #{run.run_id}</span>
                            <span className={`capitalize ${
                              run.status === 'completed' ? 'text-green-600' :
                              run.status === 'running' ? 'text-blue-600' :
                              run.status === 'failed' ? 'text-red-600' : 'text-gray-600'
                            }`}>
                              {run.status}
                            </span>
                          </div>
                          <div className="text-gray-500">
                            {run.variant_count} variants • {run.engine || 'All engines'}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}