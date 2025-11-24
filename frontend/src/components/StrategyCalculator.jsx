import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Calculator, TrendingDown, Clock, AlertTriangle } from 'lucide-react'

function StrategyCalculator({ raceId }) {
  const [currentLap, setCurrentLap] = useState(10)
  const [totalLaps, setTotalLaps] = useState(27)
  const [degradationRate, setDegradationRate] = useState(0.02)
  const [strategy, setStrategy] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    calculateStrategy()
  }, [raceId, currentLap, totalLaps, degradationRate])

  const calculateStrategy = async () => {
    if (currentLap >= totalLaps) {
      setStrategy(null)
      return
    }

    setLoading(true)
    try {
      const res = await fetch(
        `/api/race/${raceId}/strategy/pit-stop?current_lap=${currentLap}&total_laps=${totalLaps}&tire_degradation_rate=${degradationRate}`
      )
      const data = await res.json()
      setStrategy(data)
    } catch (error) {
      console.error('Error calculating strategy:', error)
    } finally {
      setLoading(false)
    }
  }

  const degradationData = strategy?.tire_degradation
    ? Object.entries(strategy.tire_degradation).map(([lap, deg]) => ({
        lap: parseInt(lap),
        degradation: deg * 100
      }))
    : []

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-3 bg-orange-100 rounded-lg">
          <Calculator className="text-orange-600" size={32} />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Pit Stop Strategy Calculator</h2>
          <p className="text-gray-600 mt-1">Calculate optimal pit stop windows based on tire degradation</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Current Lap</label>
            <input
              type="number"
              value={currentLap}
              onChange={(e) => setCurrentLap(parseInt(e.target.value) || 1)}
              min={1}
              max={totalLaps - 1}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Total Laps</label>
            <input
              type="number"
              value={totalLaps}
              onChange={(e) => setTotalLaps(parseInt(e.target.value) || 27)}
              min={currentLap + 1}
              max={100}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tire Degradation Rate (% per lap)</label>
            <input
              type="number"
              value={degradationRate * 100}
              onChange={(e) => setDegradationRate((parseFloat(e.target.value) || 0) / 100)}
              min={0.1}
              max={5}
              step={0.1}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Calculating strategy...</p>
          </div>
        </div>
      )}

      {strategy && (
        <>
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Recommended Strategy</h3>
              <span className={`px-4 py-2 rounded-lg font-semibold text-sm ${
                strategy.strategy_type === 'no_pit' ? 'bg-green-100 text-green-800' :
                strategy.strategy_type === 'one_pit' ? 'bg-blue-100 text-blue-800' :
                'bg-purple-100 text-purple-800'
              }`}>
                {strategy.strategy_type.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            
            {strategy.recommended_laps.length > 0 ? (
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Pit Stop Laps:</h4>
                <div className="flex gap-3 flex-wrap">
                  {strategy.recommended_laps.map((lap, idx) => (
                    <div key={idx} className="px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg font-semibold">
                      Lap {lap}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-6">
                <AlertTriangle className="text-yellow-600" size={24} />
                <span className="text-yellow-800 font-medium">No pit stop recommended - stay out on current tires</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                <TrendingDown className={strategy.time_gain > 0 ? "text-green-600" : "text-red-600"} size={24} />
                <div>
                  <div className="text-sm text-gray-600">Time Gain/Loss</div>
                  <div className={`text-2xl font-bold ${strategy.time_gain > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {strategy.time_gain > 0 ? '+' : ''}{strategy.time_gain.toFixed(1)}s
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                <Clock className="text-blue-600" size={24} />
                <div>
                  <div className="text-sm text-gray-600">Time Loss (vs No Pit)</div>
                  <div className="text-2xl font-bold text-gray-900">{strategy.time_loss.toFixed(1)}s</div>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Strategy Reasoning</h4>
              <p className="text-gray-700 leading-relaxed">{strategy.reasoning}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Tire Degradation Projection</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={degradationData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="lap" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ 
                    background: '#ffffff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                  formatter={(value) => `${value.toFixed(2)}%`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="degradation" 
                  stroke="#f97316" 
                  strokeWidth={3}
                  name="Tire Degradation"
                  dot={{ fill: '#f97316', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}

export default StrategyCalculator
