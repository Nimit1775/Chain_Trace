export default function RiskBadge({ score }) {
  if (score == null) return null

  const level =
    score >= 80 ? { label: 'CRITICAL', bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/40' } :
    score >= 60 ? { label: 'HIGH',     bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/40' } :
    score >= 35 ? { label: 'MEDIUM',   bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/40' } :
                  { label: 'LOW',      bg: 'bg-green-500/20',  text: 'text-green-400',  border: 'border-green-500/40' }

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            score >= 80 ? 'bg-red-500' :
            score >= 60 ? 'bg-orange-500' :
            score >= 35 ? 'bg-yellow-500' : 'bg-green-500'
          }`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className={`text-xs font-bold px-2 py-0.5 rounded border ${level.bg} ${level.text} ${level.border}`}>
        {level.label}
      </span>
      <span className="text-sm font-mono text-white/70">{score}</span>
    </div>
  )
}
