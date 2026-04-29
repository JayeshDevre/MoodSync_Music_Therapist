import SongCard from './SongCard.jsx'
import './ResultsPanel.css'

export default function ResultsPanel({ result, loading }) {
  if (loading) return (
    <div className="results-panel">
      <div className="results-loading">
        <div className="loading-spinner" />
        <div className="loading-steps">
          <div className="loading-step">🧠 Parsing your mood...</div>
          <div className="loading-step">📚 Retrieving research...</div>
          <div className="loading-step">🎵 Scoring songs...</div>
          <div className="loading-step">✨ Generating explanations...</div>
        </div>
      </div>
    </div>
  )

  if (!result) return (
    <div className="results-panel">
      <div className="results-empty">
        <div className="empty-icon">🎼</div>
        <div className="empty-title">Your recommendations will appear here</div>
        <p className="empty-sub">Tell me how you're feeling in the chat and I'll find the right music for your mood.</p>
      </div>
    </div>
  )

  const { recommendations, rag_sources, agent_retries, agent_passed, mood } = result

  return (
    <div className="results-panel">
      <div className="results-header">
        <div className="results-title">
          {recommendations.length} songs for <strong>{mood.mood}</strong> mood
        </div>
        <div className="results-badges">
          <span className={`badge ${agent_passed ? 'badge-green' : 'badge-yellow'}`}>
            {agent_passed ? '✓ Agent passed' : '↺ Agent adjusted'}
          </span>
          {agent_retries > 0 && (
            <span className="badge badge-yellow">{agent_retries} retr{agent_retries === 1 ? 'y' : 'ies'}</span>
          )}
          <span className="badge badge-purple">RAG · {rag_sources.length} sources</span>
        </div>
      </div>

      <div className="results-body">
        <div className="songs-list">
          {recommendations.map((song, i) => (
            <SongCard key={song.title} rank={i + 1} song={song} />
          ))}
        </div>

        <div className="sidebar">
          <div className="sidebar-section">
            <div className="sidebar-title">📚 Research Retrieved</div>
            {rag_sources.map(src => (
              <div key={src.source} className="rag-source">
                <div className="rag-dot" />
                <span className="rag-source-name">
                  {src.source.replace('.md', '').replace(/_/g, ' ')}
                </span>
                <span className="rag-pct">{Math.round(src.score * 100)}%</span>
              </div>
            ))}
          </div>

          <div className="sidebar-section">
            <div className="sidebar-title">🧠 Mood Analysis</div>
            <div className="mood-row">
              <span className="mood-label">Detected</span>
              <span className="mood-value">{mood.mood}</span>
            </div>
            <div className="mood-row">
              <span className="mood-label">Genre hint</span>
              <span className="mood-value">{mood.genre_hint}</span>
            </div>
            <MoodBar label="Energy" value={mood.energy} color="#7c5cbf" />
            <MoodBar label="Positivity" value={mood.valence} color="#2d7a4f" />
            <MoodBar label="Acousticness" value={mood.acousticness} color="#e8734a" />
            <p className="mood-reasoning">{mood.reasoning}</p>
          </div>

          <div className="sidebar-section">
            <div className="sidebar-title">🤖 Agent Log</div>
            <div className="agent-row">
              <span className="agent-icon">{agent_passed ? '✅' : '⚠️'}</span>
              <span>{agent_passed ? 'Self-critique passed' : 'Picks were adjusted'}</span>
            </div>
            <div className="agent-row">
              <span className="agent-icon">↺</span>
              <span>{agent_retries === 0 ? 'No retries needed' : `${agent_retries} rerank(s) performed`}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MoodBar({ label, value, color }) {
  const pct = Math.round(value * 100)
  return (
    <div className="mood-row">
      <span className="mood-label">{label}</span>
      <div className="mini-bar-wrap">
        <div className="mini-bar-track">
          <div className="mini-bar-fill" style={{ width: `${pct}%`, background: color }} />
        </div>
        <span className="mini-bar-pct">{pct}%</span>
      </div>
    </div>
  )
}
