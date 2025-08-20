import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Site {
  site_id: number
  domain: string
  cms_type?: string
}

interface ContentBlock {
  type: string
  title: string
  content: any
  word_count: number
  evaluator_score: number
}

interface Schema {
  type: string
  jsonld: any
  path: string
}

interface GenerationResponse {
  topic: string
  site_id: number
  blocks: ContentBlock[]
  schemas: Schema[]
  total_word_count: number
  generated_at: string
}

export default function Optimization() {
  const [sites, setSites] = useState<Site[]>([])
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [topic, setTopic] = useState('')
  const [formats, setFormats] = useState(['faq', 'table', 'para', 'jsonld'])
  const [generatedContent, setGeneratedContent] = useState<GenerationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [deployLoading, setDeployLoading] = useState(false)

  useEffect(() => {
    loadSites()
  }, [])

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

  const generateContent = async () => {
    if (!selectedSite || !topic.trim()) return

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8002/v1/content/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic,
          site_id: selectedSite.site_id,
          formats: formats
        })
      })

      if (response.ok) {
        const data = await response.json()
        setGeneratedContent(data)
      } else {
        alert('Content generation failed')
      }
    } catch (error) {
      console.error('Content generation error:', error)
      alert('Content generation error')
    }
    setLoading(false)
  }

  const deployToWordPress = async () => {
    if (!generatedContent || !selectedSite) return

    setDeployLoading(true)
    try {
      // First connect to WordPress (demo)
      const connectResponse = await fetch('http://localhost:8005/v1/cms/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_id: selectedSite.site_id,
          cms_type: 'wordpress',
          site_url: `https://${selectedSite.domain}`,
          username: 'admin',
          app_password: 'demo-password'
        })
      })

      if (connectResponse.ok) {
        // Deploy content
        const deployResponse = await fetch('http://localhost:8005/v1/deploy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            site_id: selectedSite.site_id,
            content_blocks: generatedContent.blocks,
            schemas: generatedContent.schemas,
            publish_immediately: false
          })
        })

        if (deployResponse.ok) {
          const deployData = await deployResponse.json()
          alert(`Successfully deployed to WordPress! Job ID: ${deployData.job_id}`)
        } else {
          alert('Deployment failed')
        }
      }
    } catch (error) {
      console.error('Deployment error:', error)
      alert('Deployment error')
    }
    setDeployLoading(false)
  }

  const formatContent = (block: ContentBlock) => {
    if (block.type === 'faq') {
      const questions = block.content.questions || []
      const answers = block.content.answers || []
      return (
        <div className="space-y-4">
          {questions.map((q: string, i: number) => (
            <div key={i} className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-semibold text-gray-900">{q}</h4>
              <p className="text-gray-700 mt-1">{answers[i]}</p>
            </div>
          ))}
        </div>
      )
    } else if (block.type === 'table') {
      const headers = block.content.headers || []
      const rows = block.content.rows || []
      return (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-300">
            <thead className="bg-gray-50">
              <tr>
                {headers.map((header: string, i: number) => (
                  <th key={i} className="px-4 py-2 border border-gray-300 text-left font-semibold">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row: string[], i: number) => (
                <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  {row.map((cell: string, j: number) => (
                    <td key={j} className="px-4 py-2 border border-gray-300 text-sm">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    } else if (block.type === 'para') {
      return (
        <div className="prose prose-sm">
          <p>{block.content.text}</p>
        </div>
      )
    }
    return <div>Unknown content type: {block.type}</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← Back to Home</Link>
              <h1 className="text-2xl font-bold text-gray-900 mt-2">LEO - Language Engine Optimization</h1>
              <p className="text-sm text-gray-500">Generate and deploy AI-optimized content</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Content Generation Form */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate AI-Optimized Content</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Topic</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., AI SEO tools, content marketing automation"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Content Formats</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { value: 'faq', label: 'FAQ Block' },
                { value: 'table', label: 'Comparison Table' },
                { value: 'para', label: 'Definition Paragraph' },
                { value: 'jsonld', label: 'JSON-LD Schema' }
              ].map(format => (
                <label key={format.value} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formats.includes(format.value)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormats([...formats, format.value])
                      } else {
                        setFormats(formats.filter(f => f !== format.value))
                      }
                    }}
                    className="mr-2"
                  />
                  <span className="text-sm">{format.label}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={generateContent}
            disabled={loading || !selectedSite || !topic.trim()}
            className="mt-6 bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Generating Content...' : 'Generate AI-Optimized Content'}
          </button>
        </div>

        {/* Generated Content Display */}
        {generatedContent && (
          <div className="space-y-6">
            
            {/* Content Overview */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Generated Content: {generatedContent.topic}</h2>
                <div className="flex space-x-3">
                  <button
                    onClick={deployToWordPress}
                    disabled={deployLoading}
                    className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700 disabled:opacity-50"
                  >
                    {deployLoading ? 'Deploying...' : 'Deploy to WordPress'}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="text-2xl font-bold text-gray-900">{generatedContent.blocks.length}</div>
                  <div className="text-sm text-gray-600">Content Blocks</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="text-2xl font-bold text-gray-900">{generatedContent.total_word_count}</div>
                  <div className="text-sm text-gray-600">Total Words</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="text-2xl font-bold text-gray-900">{generatedContent.schemas.length}</div>
                  <div className="text-sm text-gray-600">JSON-LD Schemas</div>
                </div>
              </div>
            </div>

            {/* Content Blocks */}
            {generatedContent.blocks.map((block, index) => (
              <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {block.title}
                  </h3>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500">
                      {block.word_count} words
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      block.evaluator_score >= 80 ? 'bg-green-100 text-green-800' :
                      block.evaluator_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      Score: {block.evaluator_score}
                    </span>
                  </div>
                </div>
                
                <div className="border border-gray-200 rounded-md p-4 bg-gray-50">
                  {formatContent(block)}
                </div>
              </div>
            ))}

            {/* JSON-LD Schemas */}
            {generatedContent.schemas.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">JSON-LD Schemas</h3>
                <div className="space-y-4">
                  {generatedContent.schemas.map((schema, index) => (
                    <div key={index} className="border border-gray-200 rounded-md p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">{schema.type}</span>
                        <span className="text-sm text-gray-500">{schema.path}</span>
                      </div>
                      <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                        {JSON.stringify(schema.jsonld, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}

        {!generatedContent && (
          <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Generate AI-Optimized Content</h3>
            <p className="text-gray-500 mb-4">
              Create FAQ blocks, comparison tables, definitions, and JSON-LD schemas optimized for AI engines.
            </p>
            <div className="text-sm text-gray-400">
              Select a site and topic above to get started.
            </div>
          </div>
        )}

      </div>
    </div>
  )

}