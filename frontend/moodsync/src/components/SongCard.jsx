import './SongCard.css'

const GENRE_EMOJI = {
  pop: '🎤', lofi: '☁️', rock: '🎸', classical: '🎻',
  ambient: '🌌', jazz: '🎷', electronic: '⚡', folk: '🪕',
  'r&b': '🎙️', 'hip-hop': '🎧', synthwave: '🌆', metal: '🤘',
  country: '🤠', funk: '🕺',
}

export default function SongCard({ rank, song }) {
  const emoji = GENRE_EMOJI[song.genre] || '🎵'
  const isTop = rank === 1

  return (
    <div className="song-card">
      <div className="song-card-top">
        <div className={`song-rank-badge ${isTop ? 'top' : ''}`}>
          {isTop ? '★' : `#${rank}`}
        </div>

        <div className="song-info">
          <div className="song-title">{song.title}</div>
          <div className="song-artist">{song.artist}</div>
          <div className="song-genre-tag">
            <span>{emoji}</span>
            <span>{song.genre}</span>
          </div>
        </div>

        <div className={`confidence-badge conf-${song.confidence_level}`}>
          {song.confidence_level}
        </div>
      </div>

      <div className="song-explanation">{song.explanation}</div>

      <div className="song-stats">
        <div className="stat">
          <span className="stat-label">Score</span>
          <span className="stat-value">{song.score}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Energy</span>
          <span className="stat-value">{Math.round(song.energy * 100)}%</span>
        </div>
        <div className="stat">
          <span className="stat-label">Tempo</span>
          <span className="stat-value">{song.tempo_bpm} bpm</span>
        </div>
        <div className="stat">
          <span className="stat-label">Confidence</span>
          <span className="stat-value">{Math.round(song.confidence_score * 100)}%</span>
        </div>
      </div>
    </div>
  )
}
