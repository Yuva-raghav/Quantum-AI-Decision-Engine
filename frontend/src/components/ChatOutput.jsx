import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'

export default function ChatOutput({ interpretation, reasoning, assumptions, speed = 20 }) {
  const [visibleText, setVisibleText] = useState('')

  useEffect(() => {
    const sourceText = interpretation || ''
    setVisibleText('')

    let index = 0
    const timer = setInterval(() => {
      index += 1
      setVisibleText(sourceText.slice(0, index))
      if (index >= sourceText.length) clearInterval(timer)
    }, speed)

    return () => clearInterval(timer)
  }, [interpretation, speed])

  const assumptionRows = useMemo(() => {
    if (!Array.isArray(assumptions)) return []
    return assumptions.filter(Boolean).slice(0, 4)
  }, [assumptions])

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-card rounded-2xl p-5"
    >
      <p className="mb-2 font-display text-xs uppercase tracking-[0.25em] text-cyan-100/80">AI Interpretation</p>
      <p className="leading-relaxed text-cyan-50/95">
        {visibleText}
        <span className="animate-pulse">|</span>
      </p>

      <div className="mt-4 rounded-xl border border-cyan-300/15 bg-black/25 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-cyan-100/75">AI Reasoning</p>
        <p className="mt-2 text-sm leading-relaxed text-cyan-50/90">{reasoning}</p>
      </div>

      {assumptionRows.length > 0 && (
        <div className="mt-3 rounded-xl border border-cyan-300/15 bg-black/20 p-3">
          <p className="text-xs uppercase tracking-[0.12em] text-cyan-100/75">Assumptions</p>
          <ul className="mt-2 space-y-1 text-sm text-cyan-50/85">
            {assumptionRows.map((row, idx) => (
              <li key={`${row}-${idx}`}>- {row}</li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  )
}
