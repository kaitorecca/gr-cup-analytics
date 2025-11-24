import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import DriverAnalysis from './components/DriverAnalysis'
import StrategyCalculator from './components/StrategyCalculator'
import RaceInsights from './components/RaceInsights'
import { Activity, Users, Target, BarChart3 } from 'lucide-react'

function NavLink({ to, icon: Icon, children }) {
  const location = useLocation()
  const isActive = location.pathname === to || (to !== '/' && location.pathname.startsWith(to))
  
  return (
    <Link
      to={to}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
        isActive
          ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg shadow-orange-500/30'
          : 'text-gray-700 hover:bg-gray-100 hover:text-orange-600'
      }`}
    >
      <Icon size={18} />
      {children}
    </Link>
  )
}

function App() {
  const [races, setRaces] = useState([])
  const [selectedRace, setSelectedRace] = useState('R1')

  useEffect(() => {
    fetch('/api/races')
      .then(res => res.json())
      .then(data => {
        setRaces(data.races || [])
        if (data.races && data.races.length > 0) {
          setSelectedRace(data.races[0])
        }
      })
      .catch(err => {
        console.error('Error fetching races:', err)
        // Fallback for testing
        setRaces(['R1', 'R2'])
      })
  }, [])

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100">
        <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-3">
                <div className="bg-gradient-to-r from-orange-500 to-red-500 p-2 rounded-lg">
                  <Activity className="text-white" size={24} />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  GR Cup Analytics
                </h1>
              </div>
              
              <nav className="hidden md:flex items-center gap-2">
                <NavLink to="/" icon={BarChart3}>Dashboard</NavLink>
                <NavLink to="/driver" icon={Users}>Driver Analysis</NavLink>
                <NavLink to="/strategy" icon={Target}>Strategy</NavLink>
                <NavLink to="/insights" icon={BarChart3}>Race Insights</NavLink>
              </nav>

              <div className="flex items-center gap-4">
                <select 
                  value={selectedRace} 
                  onChange={(e) => setSelectedRace(e.target.value)}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-colors"
                >
                  {races.map(race => (
                    <option key={race} value={race}>{race}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard raceId={selectedRace} />} />
            <Route path="/driver" element={<DriverAnalysis raceId={selectedRace} />} />
            <Route path="/strategy" element={<StrategyCalculator raceId={selectedRace} />} />
            <Route path="/insights" element={<RaceInsights raceId={selectedRace} />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
