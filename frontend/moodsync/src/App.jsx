import { useState } from 'react'
import ChatPanel from './components/ChatPanel.jsx'
import ResultsPanel from './components/ResultsPanel.jsx'
import './App.css'

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(userInput) {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <span className="logo">🎵 MoodSync</span>
        <span className="tagline">AI Music Therapist</span>
      </header>

      <main className="app-body">
        <ChatPanel onSubmit={handleSubmit} loading={loading} error={error} result={result} />
        {result && <ResultsPanel result={result} />}
      </main>
    </div>
  )
}
