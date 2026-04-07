import { motion } from 'framer-motion'
import { Lightbulb, Scale, ShieldCheck } from 'lucide-react'

export default function WhySolutionPanel({ text, approximationRatio, efficiencyLabel }) {
  const ratioPercent = (approximationRatio * 100).toFixed(2)

  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      className="glass-card rounded-2xl p-5"
    >
      <p className="font-display text-xs uppercase tracking-[0.25em] text-cyan-100/80">Why This Solution?</p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-cyan-200/15 bg-black/25 p-3">
          <p className="inline-flex items-center gap-1 text-[11px] uppercase tracking-[0.15em] text-cyan-100/75">
            <Lightbulb size={12} />
            Quantum Efficiency
          </p>
          <p className="mt-1 text-sm font-semibold text-white">{ratioPercent}%</p>
        </div>

        <div className="rounded-xl border border-cyan-200/15 bg-black/25 p-3">
          <p className="inline-flex items-center gap-1 text-[11px] uppercase tracking-[0.15em] text-cyan-100/75">
            <Scale size={12} />
            Approximation Class
          </p>
          <p className="mt-1 text-sm font-semibold text-white">{efficiencyLabel}</p>
        </div>

        <div className="rounded-xl border border-cyan-200/15 bg-black/25 p-3">
          <p className="inline-flex items-center gap-1 text-[11px] uppercase tracking-[0.15em] text-cyan-100/75">
            <ShieldCheck size={12} />
            Classical Optimal
          </p>
          <p className="mt-1 text-sm font-semibold text-white">Benchmark active</p>
        </div>
      </div>

      <p className="mt-4 leading-relaxed text-cyan-50/90">{text}</p>
    </motion.section>
  )
}
