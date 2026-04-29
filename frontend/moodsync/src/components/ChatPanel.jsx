import { useState, useRef, useEffect } from 'react'
import './ChatPanel.css'

const SUGGESTIONS = [
  { icon: '😰', text: "I'm stressed and can't focus" },
  { icon: '💃', text: 'Feeling happy, want to dance' },
  { icon: '😴', text: 'Exhausted, need to wind down' },
  { icon: '💪', text: 'Need energy for a workout' },
  { icon: '🌧️', text: 'Feeling nostalgic and reflective' },
]

export default function ChatPanel({ onSubmit, loading, error, result }) {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // When result arrives, add AI response to messages
  useEffect(() => {
    if (result && messages.length > 0 && messages[messages.length - 1].role === 'user') {
      setMessages(m => [...m, { role: 'ai', result }])
    }
  }, [result])

  useEffect(() => {
    if (error && messages.length > 0 && messages[messages.length - 1].role === 'user') {
      setMessages(m => [...m, { role: 'error', text: error }])
    }
  }, [error])

  function handleSend() {
    const text = input.trim()
    if (!text || loading) return
    setMessages(m => [...m, { role: 'user', text }])
    setInput('')
    onSubmit(text)
  }

  function handleSuggestion(text) {
    setInput(text)
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <div className="welcome-avatar">🎧</div>
            <div className="welcome-title">How are you feeling?</div>
            <p className="welcome-sub">
              Describe your mood and I'll find music that fits — backed by music psychology research.
            </p>
            <div className="suggestions-label">Try one of these</div>
            <div className="suggestions">
              {SUGGESTIONS.map(s => (
                <button key={s.text} className="suggestion-chip" onClick={() => handleSuggestion(s.text)}>
                  <span>{s.icon}</span>
                  <span>{s.text}</span>
                  <span className="chip-arrow">→</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => {
          if (msg.role === 'user') return (
            <div key={i} className="message message-user">
              <div className="message-meta">You</div>
              <div className="message-bubble">{msg.text}</div>
            </div>
          )

          if (msg.role === 'ai') return (
            <div key={i} className="message message-ai">
              <div className="message-meta">MoodSync</div>
              <div className="message-bubble">
                <div className="ai-intro">
                  Found <strong>{msg.result.recommendations.length} songs</strong> for your{' '}
                  <strong>{msg.result.mood.mood}</strong> mood ↓
                </div>
                <div className="mood-pills">
                  <span className="mood-pill accent">{msg.result.mood.genre_hint}</span>
                  <span className="mood-pill">energy {Math.round(msg.result.mood.energy * 100)}%</span>
                  <span className="mood-pill">valence {Math.round(msg.result.mood.valence * 100)}%</span>
                  {msg.result.agent_retries > 0 && (
                    <span className="mood-pill">↺ reranked</span>
                  )}
                </div>
                {msg.result.needs_clarification && (
                  <span className="clarify-note">⚠ Low confidence — could you describe your mood in more detail?</span>
                )}
              </div>
            </div>
          )

          if (msg.role === 'error') return (
            <div key={i} className="message message-ai">
              <div className="message-bubble error-bubble">⚠ {msg.text}</div>
            </div>
          )
        })}

        {loading && (
          <div className="message message-ai">
            <div className="message-meta">MoodSync</div>
            <div className="message-bubble loading-bubble">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <div className="input-wrapper">
          <textarea
            className="chat-input"
            placeholder="Describe how you're feeling..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            rows={1}
            disabled={loading}
          />
          <button className="send-btn" onClick={handleSend} disabled={loading || !input.trim()}>
            ↑
          </button>
        </div>
        <div className="input-hint">Press Enter to send · Shift+Enter for new line</div>
      </div>
    </div>
  )
}
