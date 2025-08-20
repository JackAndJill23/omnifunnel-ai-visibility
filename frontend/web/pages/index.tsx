import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function Home() {
	const [services, setServices] = useState({
		tracker: null,
		generator: null,
		analytics: null,
		score: null,
		deployer: null,
		telemetry: null,
		billing: null,
	})

	const [engines, setEngines] = useState([])

	useEffect(() => {
		const check = async (name, url) => {
			try {
				const res = await fetch(url)
				const json = await res.json()
				setServices((s) => ({ ...s, [name]: json }))
			} catch (e) {
				setServices((s) => ({ ...s, [name]: { status: 'down', service: name } }))
			}
		}

		const checkEngines = async () => {
			try {
				const res = await fetch('http://localhost:8001/v1/engines')
				const json = await res.json()
				setEngines(json.engines || [])
			} catch (e) {
				console.error('Failed to load engines:', e)
			}
		}

		check('tracker', 'http://localhost:8001/health')
		check('generator', 'http://localhost:8002/health')
		check('analytics', 'http://localhost:8003/health')
		check('score', 'http://localhost:8004/health')
		check('deployer', 'http://localhost:8005/health')
		check('telemetry', 'http://localhost:8006/health')
		check('billing', 'http://localhost:8007/health')
		checkEngines()
	}, [])

	return (
		<div className="min-h-screen bg-gray-50">
			{/* Header */}
			<div className="bg-white shadow-sm border-b">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div className="flex justify-between items-center py-6">
						<div>
							<h1 className="text-3xl font-bold text-gray-900">OmniFunnel AI Visibility</h1>
							<p className="mt-1 text-sm text-gray-500">AI-native SEO platform for tracking brand visibility across LLMs</p>
						</div>
						<div className="flex space-x-4">
							<Link href="/master-dashboard" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:from-blue-700 hover:to-purple-700">
								Master Control
							</Link>
							<Link href="/scores" className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
								AI Score™
							</Link>
							<Link href="/optimization" className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700">
								LEO
							</Link>
							<Link href="/intelligence" className="bg-purple-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-purple-700">
								Intel
							</Link>
						</div>
					</div>
				</div>
			</div>

			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
					
					{/* Service Status */}
					<div className="bg-white rounded-lg shadow-sm border p-6">
						<h2 className="text-xl font-semibold text-gray-900 mb-4">Service Status</h2>
						<div className="space-y-3">
							{Object.entries(services).map(([name, service]) => (
								<div key={name} className="flex items-center justify-between">
									<div className="flex items-center space-x-3">
										<div className={`w-3 h-3 rounded-full ${
											service?.status === 'ok' ? 'bg-green-400' : 
											service?.status === 'down' ? 'bg-red-400' : 'bg-gray-300'
										}`} />
										<span className="text-sm font-medium text-gray-900 capitalize">{name}</span>
									</div>
									<span className={`text-sm font-medium ${
										service?.status === 'ok' ? 'text-green-600' : 
										service?.status === 'down' ? 'text-red-600' : 'text-gray-500'
									}`}>
										{service ? service.status : 'checking...'}
									</span>
								</div>
							))}
						</div>
					</div>

					{/* AI Engines */}
					<div className="bg-white rounded-lg shadow-sm border p-6">
						<h2 className="text-xl font-semibold text-gray-900 mb-4">AI Engines</h2>
						{engines.length > 0 ? (
							<div className="grid grid-cols-2 gap-3">
								{engines.map((engine) => (
									<div key={engine} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-md">
										<div className="w-2 h-2 bg-green-400 rounded-full" />
										<span className="text-sm font-medium text-gray-900 capitalize">{engine}</span>
									</div>
								))}
							</div>
						) : (
							<p className="text-gray-500 text-sm">Loading engines...</p>
						)}
						<div className="mt-4 text-xs text-gray-500">
							{engines.length} engines configured with API keys
						</div>
					</div>

					{/* Quick Actions */}
					<div className="bg-white rounded-lg shadow-sm border p-6">
						<h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
						<div className="space-y-3">
							<Link href="/tracking" className="block w-full text-left p-3 border border-gray-200 rounded-md hover:border-blue-300 hover:bg-blue-50 transition-colors">
								<div className="font-medium text-gray-900">Create Site</div>
								<div className="text-sm text-gray-500">Add a new website for AI visibility tracking</div>
							</Link>
							<Link href="/tracking" className="block w-full text-left p-3 border border-gray-200 rounded-md hover:border-blue-300 hover:bg-blue-50 transition-colors">
								<div className="font-medium text-gray-900">Create Cluster</div>
								<div className="text-sm text-gray-500">Set up prompt clusters for keyword tracking</div>
							</Link>
							<Link href="/dashboard" className="block w-full text-left p-3 border border-gray-200 rounded-md hover:border-blue-300 hover:bg-blue-50 transition-colors">
								<div className="font-medium text-gray-900">View Results</div>
								<div className="text-sm text-gray-500">Monitor tracking runs and results</div>
							</Link>
							<Link href="/scores" className="block w-full text-left p-3 border border-gray-200 rounded-md hover:border-blue-300 hover:bg-blue-50 transition-colors">
								<div className="font-medium text-gray-900">AI Visibility Score™</div>
								<div className="text-sm text-gray-500">Calculate and view performance metrics</div>
							</Link>
						</div>
					</div>

					{/* Getting Started */}
					<div className="bg-white rounded-lg shadow-sm border p-6">
						<h2 className="text-xl font-semibold text-gray-900 mb-4">Getting Started</h2>
						<div className="space-y-4">
							<div className="flex items-start space-x-3">
								<div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">1</div>
								<div>
									<div className="font-medium text-gray-900">Create a Site</div>
									<div className="text-sm text-gray-500">Add your domain for tracking</div>
								</div>
							</div>
							<div className="flex items-start space-x-3">
								<div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">2</div>
								<div>
									<div className="font-medium text-gray-900">Set Up Clusters</div>
									<div className="text-sm text-gray-500">Define keyword groups and seed prompts</div>
								</div>
							</div>
							<div className="flex items-start space-x-3">
								<div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">3</div>
								<div>
									<div className="font-medium text-gray-900">Run Tracking</div>
									<div className="text-sm text-gray-500">Start monitoring AI engine responses</div>
								</div>
							</div>
							<div className="flex items-start space-x-3">
								<div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">4</div>
								<div>
									<div className="font-medium text-gray-900">Analyze Results</div>
									<div className="text-sm text-gray-500">Review citations and AI Visibility Score</div>
								</div>
							</div>
						</div>
					</div>

				</div>

				{/* Status Banner */}
				<div className="mt-8 bg-green-50 border border-green-200 rounded-md p-4">
					<div className="flex">
						<div className="flex-shrink-0">
							<svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
								<path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
							</svg>
						</div>
						<div className="ml-3">
							<p className="text-sm text-green-800">
								<strong>System Ready:</strong> All AI engines configured with API keys. Tracker service is operational and ready for AI visibility monitoring.
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	)
}
