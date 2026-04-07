import { motion } from 'framer-motion'

export default function Loader() {
  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center gap-4">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1.1, repeat: Infinity, ease: 'linear' }}
          className="h-10 w-10 rounded-full border-2 border-cyan-200/20 border-t-cyanGlow"
        />

        <div className="w-full">
          <p className="font-display text-xs uppercase tracking-[0.25em] text-cyan-100/75">Running quantum simulation...</p>
          <div className="mt-3 flex gap-2">
            {[0, 1, 2, 3].map((idx) => (
              <motion.div
                key={idx}
                animate={{ opacity: [0.25, 1, 0.25], scaleY: [0.8, 1.25, 0.8] }}
                transition={{ duration: 1, delay: idx * 0.15, repeat: Infinity }}
                className="h-4 w-full rounded bg-gradient-to-b from-cyanGlow to-blueGlow"
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
