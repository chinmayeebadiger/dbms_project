import { Routes, Route } from 'react-router-dom'
import AppShell from './components/AppShell'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'
import Report from './pages/Report'
import History from './pages/History'
import Graph from './pages/Graph'

export default function App() {
  return <AppShell><Routes><Route path="/" element={<Dashboard />} /><Route path="/analyze" element={<Analyze />} /><Route path="/report" element={<Report />} /><Route path="/history" element={<History />} /><Route path="/history/:id" element={<Report />} /><Route path="/graph" element={<Graph />} /><Route path="*" element={<Dashboard />} /></Routes></AppShell>
}
