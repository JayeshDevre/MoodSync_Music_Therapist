import { useState } from 'react'
import './ChatPanel.css'

const SUGGESTIONS = [
  "I'm stressed and can't focus",
  "Feeling happy, want to dance",
  "Exhausted after a long day",
  "Need motivation for a workout",
  "Feeling nostalgic and reflective",
]

export default function ChatPanel({ onSubmit, loading, error, result }) {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState([])

  function handleSend() {
    const text = input.trim()
    if (!text || loading) return
    setHistory(h => [...h, { role: 'user', text }])
    setInput('')
    onSubmit(text)
  }

  function handleSuggestion(s) {
    setInput(s)
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Add AI response to history when result arrives
  const lastUserMsg = history[history.length - 1]
  const showAiResponse = result && lastUserMsg?.role === 'user'

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {history.length === 0 && (
          <div className="chat-welcome">
            <div className="welcome-icon">🎧</div>
            <p>Tell me how you're feeling and I'll find the perfect music for your mood.</p>
            <div className="suggestions">
              {SUGGESTIONS.map(s => (
                <button key={s} className="suggestion-chip" onClick={() => handleSuggestion(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {history.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            <span className="message-bubble">{msg.text}</span>
          </div>
        ))}

        {loading && (
          <div className="message message-ai">
            <span className="message-bubble loading-bubble">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </span>
          </div>
        )}

        {showAiResponse && !loading && result && (
          <div className="message message-ai">
            <span className="message-bubble ai-response">
              I found <strong>{result.recommendations.length} songs</strong> for your <strong>{result.mood.mood}</strong> mood.
              {result.needs_clarification && (
                <span className="clarify-note"> Could you tell me more about what you need?</span>
              )}
              <div className="mood-tags">
                <span className="tag">energy {result.mood.energy}</span>
                <span className="tag">valence {result.mood.valence}</span>
                <span className="tag">{result.mood.genre_hint}</span>
              </div>
            </span>
          </div>
        )}

        {error && (
          <div className="message message-ai">
            <span className="message-bubble error-bubble">⚠ {error}</span>
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <textarea
          className="chat-input"
          placeholder="How are you feeling right now?"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          rows={2}
          disabled={loading}
        />
        <button className="send-btn" onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? '...' : '→'}
        </button>
      </div>
    </div>
  )
}
