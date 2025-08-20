import { useState, useEffect } from 'react'
import Link from 'next/link'

interface ServiceHealth {
  service: string
  status: string
  port: number
  features?: string[]
}

interface PlatformMetrics {
  sites_tracked: number
  clusters_active: number
  ai_engines_connected: number
  content_blocks_generated: number
  deployments_completed: number
  competitive_analyses: number
}

export default function MasterDashboard() {
  const [services, setServices] = useState<ServiceHealth[]>([])
  const [metrics, setMetrics] = useState<PlatformMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadServiceHealth()
    loadPlatformMetrics()
  }, [])

  const loadServiceHealth = async () => {
    const serviceEndpoints = [
      { name: 'Tracker', port: 8001, path: '/health' },
      { name: 'Generator', port: 8002, path: '/health' },
      { name: 'Analytics', port: 8003, path: '/health' },
      { name: 'Score', port: 8004, path: '/health' },
      { name: 'Deployer', port: 8005, path: '/health' },
      { name: 'GEO', port: 8006, path: '/health' }
    ]

    const healthChecks = await Promise.all(
      serviceEndpoints.map(async (service) => {
        try {
          const response = await fetch(`http://localhost:${service.port}${service.path}`)
          if (response.ok) {
            const data = await response.json()
            return {
              service: service.name,
              status: data.status || 'ok',
              port: service.port,
              features: data.features || data.engines || []
            }
          } else {
            return {
              service: service.name,
              status: 'down',
              port: service.port,
              features: []
            }
          }
        } catch (error) {
          return {
            service: service.name,
            status: 'error',
            port: service.port,
            features: []
          }
        }
      })
    )

    setServices(healthChecks)
  }

  const loadPlatformMetrics = async () => {
    try {
      // Get sites count
      const sitesResponse = await fetch('http://localhost:8001/v1/sites?tenant_id=1')
      const sites = sitesResponse.ok ? await sitesResponse.json() : []

      // Get engines count
      const enginesResponse = await fetch('http://localhost:8001/v1/engines')
      const engines = enginesResponse.ok ? await enginesResponse.json() : { engines: [] }

      // Simulate other metrics
      setMetrics({
        sites_tracked: sites.length,
        clusters_active: sites.length * 2, // Estimate
        ai_engines_connected: engines.engines?.length || 5,
        content_blocks_generated: 15, // Would query generator service
        deployments_completed: 3, // Would query deployer service
        competitive_analyses: 2 // Would query analytics service
      })

    } catch (error) {
      console.error('Failed to load platform metrics:', error)
    }
    setLoading(false)
  }

  const getServiceStatusColor = (status: string) => {
    if (status === 'ok') return 'bg-green-100 text-green-800'
    if (status === 'down') return 'bg-red-100 text-red-800'
    return 'bg-yellow-100 text-yellow-800'
  }

  const runFullPlatformDemo = async () => {
    // Demonstrate the complete platform workflow
    alert('Running complete platform demonstration...')
    
    try {
      // 1. Create demo site
      const siteResponse = await fetch('http://localhost:8001/v1/sites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          domain: 'demo-platform.com',
          cms_type: 'wordpress',
          tenant_id: 1
        })
      })
      
      if (siteResponse.ok) {
        const site = await siteResponse.json()
        
        // 2. Create cluster
        const clusterResponse = await fetch(`http://localhost:8001/v1/sites/${site.site_id}/clusters`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'Complete Demo Cluster',
            seed_prompt: 'comprehensive AI marketing platform',
            keywords: ['ai', 'marketing', 'automation']
          })
        })
        
        if (clusterResponse.ok) {
          const cluster = await clusterResponse.json()
          
          // 3. Generate content
          const contentResponse = await fetch('http://localhost:8002/v1/content/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              topic: 'AI marketing automation',
              site_id: site.site_id,
              formats: ['faq', 'table', 'para', 'jsonld']
            })
          })
          
          // 4. Run AI tracking
          const trackingResponse = await fetch(`http://localhost:8001/v1/clusters/${cluster.cluster_id}/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              engine: 'chatgpt',
              variant_sample: 2
            })
          })
          
          // 5. Calculate score
          const scoreResponse = await fetch('http://localhost:8004/v1/calculate-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              site_id: site.site_id,
              cluster_id: cluster.cluster_id,
              date_range_days: 30
            })
          })
          
          if (scoreResponse.ok) {
            const score = await scoreResponse.json()
            alert(`Demo completed! AI Visibility Score: ${score.total}/100`)
            
            // Refresh metrics
            loadPlatformMetrics()
          }
        }
      }
    } catch (error) {
      console.error('Demo error:', error)
      alert('Demo encountered an error')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← Back to Home</Link>
              <h1 className="text-2xl font-bold text-gray-900 mt-2">Master Control Dashboard</h1>
              <p className="text-sm text-gray-500">Complete platform overview and control center</p>
            </div>
            <button
              onClick={runFullPlatformDemo}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-md font-medium hover:from-blue-700 hover:to-purple-700"
            >
              Run Complete Demo
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Platform Metrics */}
        {metrics && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-sm border p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{metrics.sites_tracked}</div>
              <div className="text-xs text-gray-600">Sites Tracked</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{metrics.clusters_active}</div>
              <div className="text-xs text-gray-600">Active Clusters</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{metrics.ai_engines_connected}</div>
              <div className="text-xs text-gray-600">AI Engines</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">{metrics.content_blocks_generated}</div>
              <div className="text-xs text-gray-600">Content Blocks</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4 text-center">
              <div className="text-2xl font-bold text-red-600">{metrics.deployments_completed}</div>
              <div className="text-xs text-gray-600">Deployments</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4 text-center">
              <div className="text-2xl font-bold text-indigo-600">{metrics.competitive_analyses}</div>
              <div className="text-xs text-gray-600">Competitor Analyses</div>
            </div>
          </div>
        )}

        {/* Service Status Grid */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Microservices Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map((service) => (
              <div key={service.service} className="border border-gray-200 rounded-md p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{service.service}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getServiceStatusColor(service.status)}`}>
                    {service.status}
                  </span>
                </div>
                <div className="text-xs text-gray-500">Port: {service.port}</div>
                {service.features && service.features.length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs text-gray-400 mb-1">Features:</div>
                    <div className="flex flex-wrap gap-1">
                      {service.features.slice(0, 3).map((feature, i) => (
                        <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Feature Access Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <Link href="/tracking" className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  🎯
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">LM SEO Tracking</h3>
                <p className="text-sm text-gray-500">Track citations across 5 AI engines</p>
              </div>
            </div>
          </Link>

          <Link href="/optimization" className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  ⚙️
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">LEO Content Engine</h3>
                <p className="text-sm text-gray-500">Generate AI-optimized content</p>
              </div>
            </div>
          </Link>

          <Link href="/intelligence" className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  🧠
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Competitive Intel</h3>
                <p className="text-sm text-gray-500">Track competitors & entities</p>
              </div>
            </div>
          </Link>

          <Link href="/scores" className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                  🏆
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">AI Visibility Score™</h3>
                <p className="text-sm text-gray-500">Proprietary performance metric</p>
              </div>
            </div>
          </Link>

        </div>

        {/* Platform Capabilities Overview */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Complete Platform Capabilities</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* LM SEO */}
            <div className="space-y-3">
              <h3 className="font-semibold text-blue-600">LM SEO (Large Model SEO)</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>✅ LLM Citation Tracker (5 engines)</li>
                <li>✅ Prompt-SoV measurement</li>
                <li>✅ Real-time answer monitoring</li>
                <li>✅ Citation extraction & analysis</li>
                <li>✅ Engine performance comparison</li>
              </ul>
            </div>

            {/* LEO */}
            <div className="space-y-3">
              <h3 className="font-semibold text-green-600">LEO (Language Engine Optimization)</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>✅ Content structuring engine</li>
                <li>✅ FAQ block generation</li>
                <li>✅ Comparison table creation</li>
                <li>✅ JSON-LD schema auto-generation</li>
                <li>✅ Content quality evaluation</li>
              </ul>
            </div>

            {/* GEO */}
            <div className="space-y-3">
              <h3 className="font-semibold text-purple-600">GEO (Generative Engine Optimization)</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>✅ AI Overviews trigger detection</li>
                <li>✅ SGE monitoring</li>
                <li>✅ Bing Copilot tracking</li>
                <li>✅ Content gap analysis</li>
                <li>✅ Auto-optimization recommendations</li>
              </ul>
            </div>

            {/* Competitive Intelligence */}
            <div className="space-y-3">
              <h3 className="font-semibold text-red-600">Competitive Intelligence</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>✅ Competitor mention tracking</li>
                <li>✅ Citation source analysis</li>
                <li>✅ Engine presence comparison</li>
                <li>✅ Performance delta alerts</li>
                <li>✅ Strategic recommendations</li>
              </ul>
            </div>

            {/* CMS Integration */}
            <div className="space-y-3">
              <h3 className="font-semibold text-orange-600">CMS Auto-Deployment</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>✅ WordPress plugin integration</li>
                <li>✅ Content auto-publishing</li>
                <li>✅ Schema deployment</li>
                <li>✅ AI map endpoint creation</li>
                <li>✅ Version control & rollback</li>
              </ul>
            </div>

            {/* Analytics & Attribution */}
            <div className="space-y-3">
              <h3 className="font-semibold text-indigo-600">Analytics & Attribution</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>✅ AI Visibility Score™ calculation</li>
                <li>✅ Entity stitching & SameAs links</li>
                <li>✅ Performance monitoring</li>
                <li>✅ ROI measurement framework</li>
                <li>✅ Executive dashboards</li>
              </ul>
            </div>

          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Platform Workflow</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-xl">1</div>
              <div className="text-sm font-medium">Track AI Presence</div>
              <div className="text-xs text-gray-600 mt-1">Monitor brand visibility across AI engines</div>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-xl">2</div>
              <div className="text-sm font-medium">Generate Content</div>
              <div className="text-xs text-gray-600 mt-1">Create AI-optimized FAQ, tables, schemas</div>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-xl">3</div>
              <div className="text-sm font-medium">Deploy to CMS</div>
              <div className="text-xs text-gray-600 mt-1">Auto-publish to WordPress/Webflow</div>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-xl">4</div>
              <div className="text-sm font-medium">Measure Impact</div>
              <div className="text-xs text-gray-600 mt-1">Calculate AI Visibility Score™</div>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-red-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-xl">5</div>
              <div className="text-sm font-medium">Optimize & Scale</div>
              <div className="text-xs text-gray-600 mt-1">Competitive analysis & improvements</div>
            </div>

          </div>
        </div>

      </div>
    </div>
  )
}