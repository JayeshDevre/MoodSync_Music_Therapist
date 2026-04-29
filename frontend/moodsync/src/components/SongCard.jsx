import './SongCard.css'

const CONFIDENCE_COLORS = {
  HIGH:   { bg: '#052e16', border: '#166534', text: '#4ade80' },
  MEDIUM: { bg: '#1c1917', border: '#44403c', text: '#a8a29e' },
  LOW:    { bg: '#2d1515', border: '#7f1d1d', text: '#f87171' },
}

const GENRE_EMOJI = {
  pop: '🎤', lofi: '☁️', rock: '🎸', classical: '🎻',
  ambient: '🌌', jazz: '🎷', electronic: '⚡', folk: '🪕',
  'r&b': '🎙️', 'hip-hop': '🎧', synthwave: '🌆', metal: '🤘',
  country: '🤠', funk: '🕺',
}

export default function SongCard({ rank, song }) {
  const conf = CONFIDENCE_COLORS[song.confidence_level] || CONFIDENCE_COLORS.MEDIUM
  const emoji = GENRE_EMOJI[song.genre] || '🎵'

  return (
    <div className="song-card">
      <div className="song-rank">#{rank}</div>

      <div className="song-main">
        <div className="song-top">
          <div className="song-info">
            <span className="song-genre-icon">{emoji}</span>
            <div>
              <div className="song-title">{song.title}</div>
              <div className="song-artist">{song.artist} · {song.genre}</div>
            </div>
          </div>
          <div
            className="confidence-badge"
            style={{ background: conf.bg, border: `1px solid ${conf.border}`, color: conf.text }}
          >
            {song.confidence_level}
          </div>
        </div>

        <div className="song-explanation">{song.explanation}</div>

        <div className="song-stats">
          <Stat label="Score" value={`${song.score} / 7.5`} />
          <Stat label="Energy" value={`${Math.round(song.energy * 100)}%`} />
          <Stat label="Tempo" value={`${song.tempo_bpm} bpm`} />
          <Stat label="Confidence" value={`${Math.round(song.confidence_score * 100)}%`} />
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
    </div>
  )
}
