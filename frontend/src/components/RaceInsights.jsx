import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Lightbulb, TrendingUp, Award, AlertCircle, Target } from 'lucide-react'

function RaceInsights({ raceId }) {
  const [insights, setInsights] = useState([])
  const [drivers, setDrivers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInsights()
    loadDrivers()
  }, [raceId])

  const loadInsights = async () => {
    try {
      const res = await fetch(`/api/race/${raceId}/insights`)
      const data = await res.json()
      setInsights(data.insights || [])
      setLoading(false)
    } catch (error) {
      console.error('Error loading insights:', error)
      setLoading(false)
    }
  }

  const loadDrivers = async () => {
    try {
      const res = await fetch(`/api/race/${raceId}/drivers`)
      const data = await res.json()
      setDrivers(data.drivers || [])
    } catch (error) {
      console.error('Error loading drivers:', error)
    }
  }

  const getInsightIcon = (type) => {
    switch (type) {
      case 'performance':
        return <TrendingUp size={24} className="text-green-600" />
      case 'consistency':
        return <Target size={24} className="text-blue-600" />
      case 'strategy':
        return <Lightbulb size={24} className="text-yellow-600" />
      default:
        return <AlertCircle size={24} className="text-orange-600" />
    }
  }

  const leaderboardData = drivers.slice(0, 10).map((driver, idx) => ({
    position: idx + 1,
    driver: `#${driver.number}`,
    bestLap: parseFloat(driver.best_lap) || 0
  }))

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading race insights...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-3 bg-orange-100 rounded-lg">
          <Lightbulb className="text-orange-600" size={32} />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Race Insights & Analysis</h2>
          <p className="text-gray-600 mt-1">Key moments and performance highlights from {raceId}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {insights.map((insight, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-gray-100 rounded-lg">
                {getInsightIcon(insight.type)}
              </div>
              <div className="flex-1">
                <div className="text-xs font-semibold text-gray-500 uppercase">{insight.type}</div>
                <div className={`text-xs font-semibold ${
                  insight.impact === 'high' ? 'text-red-600' :
                  insight.impact === 'medium' ? 'text-yellow-600' :
                  'text-blue-600'
                }`}>
                  {insight.impact.toUpperCase()} IMPACT
                </div>
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{insight.title}</h3>
            <p className="text-sm text-gray-600 mb-4">{insight.description}</p>
            {insight.driver && (
              <div className="flex items-center gap-2 px-3 py-2 bg-orange-50 border border-orange-200 rounded-lg">
                <Award className="text-orange-600" size={16} />
                <span className="text-sm font-medium text-orange-800">Driver #{insight.driver}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {drivers.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Top 10 Leaderboard</h3>
          <div className="mb-6">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={leaderboardData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  type="number" 
                  stroke="#6b7280"
                  label={{ value: 'Best Lap Time', position: 'insideBottom', offset: -5 }}
                  domain={(() => {
                    // Calculate dynamic domain based on actual data to show differences clearly
                    const validLaps = leaderboardData.filter(d => d.bestLap > 0).map(d => d.bestLap)
                    if (validLaps.length === 0) return [90, 100]
                    
                    const minTime = Math.min(...validLaps)
                    const maxTime = Math.max(...validLaps)
                    const range = maxTime - minTime
                    
                    // Add padding: 10% of range, or minimum 0.5 seconds
                    const padding = Math.max(range * 0.1, 0.5)
                    
                    // Round down min and round up max for clean axis labels
                    const domainMin = Math.floor((minTime - padding) * 10) / 10
                    const domainMax = Math.ceil((maxTime + padding) * 10) / 10
                    
                    return [domainMin, domainMax]
                  })()}
                  tickFormatter={(value) => {
                    // Format as MM:SS.mmm for better readability
                    const minutes = Math.floor(value / 60)
                    const seconds = (value % 60).toFixed(3)
                    return `${minutes}:${seconds.padStart(6, '0')}`
                  }}
                />
                <YAxis dataKey="driver" type="category" stroke="#6b7280" width={80} />
                <Tooltip 
                  contentStyle={{ 
                    background: '#ffffff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                  formatter={(value) => formatLapTime(value)}
                />
                <Bar dataKey="bestLap" fill="#f97316" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Driver #</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vehicle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Best Lap</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Time</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {drivers.slice(0, 10).map((driver, idx) => (
                  <tr key={driver.id} className={idx < 3 ? 'bg-yellow-50' : 'hover:bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-semibold">
                        {idx + 1}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{driver.number}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{driver.vehicle}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{driver.class}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{driver.best_lap || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{driver.total_time || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {insights.length === 0 && (
        <div className="bg-white rounded-xl shadow-lg p-12 border border-gray-100 text-center">
          <AlertCircle className="text-gray-400 mx-auto mb-4" size={48} />
          <p className="text-gray-600">No insights available for this race yet.</p>
        </div>
      )}
    </div>
  )
}

function formatLapTime(seconds) {
  if (!seconds || seconds === 0) return 'N/A'
  const minutes = Math.floor(seconds / 60)
  const secs = (seconds % 60).toFixed(3)
  return `${minutes}:${secs.padStart(6, '0')}`
}

export default RaceInsights
