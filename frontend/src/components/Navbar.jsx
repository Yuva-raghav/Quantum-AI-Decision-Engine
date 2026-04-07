import { motion } from 'framer-motion'
import { Cpu, Sparkles } from 'lucide-react'

export default function Navbar() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: 'easeOut' }}
      className="sticky top-0 z-40 border-b border-cyan-300/15 bg-black/20 backdrop-blur-xl"
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="rounded-full border border-cyan-300/40 bg-cyan-300/10 p-2 shadow-neon">
            <Cpu size={18} className="text-cyanGlow" />
          </div>
          <div>
            <p className="font-display text-sm uppercase tracking-[0.32em] text-cyan-100/80">Quantum-AI</p>
            <p className="font-display text-lg font-semibold text-white">Decision Engine</p>
          </div>
        </div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="inline-flex items-center gap-2 rounded-full border border-violet-300/40 bg-violet-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-violet-100 shadow-violet"
        >
          <Sparkles size={14} />
          Premium Simulation
        </motion.div>
      </div>
    </motion.header>
  )
}
