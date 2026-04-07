import { motion } from 'framer-motion'
import { useState } from 'react'
import { Wand2 } from 'lucide-react'

export default function InputBox({ onSubmit, loading, initialValue }) {
  const [prompt, setPrompt] = useState(initialValue)
  const [ripples, setRipples] = useState([])

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!prompt.trim() || loading) return
    onSubmit(prompt.trim())
  }

  const triggerRipple = (event) => {
    const rect = event.currentTarget.getBoundingClientRect()
    const ripple = {
      id: Date.now(),
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    }
    setRipples((prev) => [...prev, ripple])
    setTimeout(() => {
      setRipples((prev) => prev.filter((item) => item.id !== ripple.id))
    }, 700)
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.15 }}
      className="glass-card relative overflow-hidden rounded-3xl p-6 shadow-neon"
    >
      <label htmlFor="prompt" className="mb-3 block font-display text-xs uppercase tracking-[0.25em] text-cyan-100/80">
        Optimization Prompt
      </label>

      <textarea
        id="prompt"
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        placeholder="Example: We have 7 delivery routes with profit and fuel cost. Budget limit is 18. Maximize profit."
        className="h-36 w-full resize-none rounded-2xl border border-cyan-200/20 bg-black/30 px-4 py-3 font-body text-sm text-white outline-none transition focus:border-cyanGlow/70 focus:shadow-[0_0_0_2px_rgba(6,247,255,0.18)]"
      />

      <div className="mt-4 flex items-center justify-between gap-4">
        <p className="text-xs text-cyan-100/70">Natural language to AI interpretation + quantum/classical comparison</p>

        <motion.button
          whileHover={{ scale: 1.04, boxShadow: '0 0 30px rgba(6,247,255,0.35)' }}
          whileTap={{ scale: 0.96 }}
          onClick={triggerRipple}
          type="submit"
          disabled={loading}
          className="relative overflow-hidden rounded-xl border border-cyanGlow/60 bg-gradient-to-r from-cyanGlow/30 to-blueGlow/25 px-5 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          <span className="relative z-10 inline-flex items-center gap-2">
            <Wand2 size={14} />
            {loading ? 'Analyzing...' : 'Run Engine'}
          </span>

          {ripples.map((ripple) => (
            <motion.span
              key={ripple.id}
              initial={{ width: 0, height: 0, opacity: 0.65 }}
              animate={{ width: 240, height: 240, opacity: 0 }}
              transition={{ duration: 0.65, ease: 'easeOut' }}
              style={{ left: ripple.x, top: ripple.y }}
              className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-100/50"
            />
          ))}
        </motion.button>
      </div>
    </motion.form>
  )
}
