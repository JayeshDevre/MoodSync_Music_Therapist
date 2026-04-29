import SongCard from './SongCard.jsx'
import './ResultsPanel.css'

export default function ResultsPanel({ result }) {
  if (!result) return null

  const { recommendations, rag_sources, agent_retries, agent_passed, mood } = result

  return (
    <div className="results-panel">
      <div className="results-header">
        <div className="results-title">Recommendations</div>
        <div className="results-meta">
          <span className="meta-badge">🤖 Agent {agent_passed ? 'passed' : 'adjusted'}</span>
          {agent_retries > 0 && <span className="meta-badge retry">↺ {agent_retries} retry</span>}
        </div>
      </div>

      <div className="results-body">
        <div className="songs-list">
          {recommendations.map((song, i) => (
            <SongCard key={song.title} rank={i + 1} song={song} />
          ))}
        </div>

        <div className="rag-panel">
          <div className="rag-title">📚 Research Retrieved</div>
          <p className="rag-subtitle">Sources the AI used to justify these picks</p>
          {rag_sources.map(src => (
            <div key={src.source} className="rag-source">
              <span className="rag-source-name">{src.source.replace('.md', '').replace(/_/g, ' ')}</span>
              <span className="rag-score">relevance {(src.score * 100).toFixed(0)}%</span>
            </div>
          ))}

          <div className="mood-breakdown">
            <div className="rag-title" style={{ marginTop: '20px' }}>🧠 Mood Analysis</div>
            <div className="mood-row"><span>Detected mood</span><strong>{mood.mood}</strong></div>
            <div className="mood-row"><span>Energy</span><MiniBar value={mood.energy} /></div>
            <div className="mood-row"><span>Positivity</span><MiniBar value={mood.valence} /></div>
            <div className="mood-row"><span>Acousticness</span><MiniBar value={mood.acousticness} /></div>
            <div className="mood-row reasoning"><span>{mood.reasoning}</span></div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MiniBar({ value }) {
  const pct = Math.round(value * 100)
  const color = value > 0.65 ? '#a78bfa' : value > 0.35 ? '#60a5fa' : '#94a3b8'
  return (
    <div className="mini-bar-wrap">
      <div className="mini-bar" style={{ width: `${pct}%`, background: color }} />
      <span className="mini-bar-label">{pct}%</span>
    </div>
  )
}
