import { motion } from 'framer-motion'
import { useMemo } from 'react'

export default function AnimatedBackground() {
  const particles = useMemo(
    () =>
      Array.from({ length: 28 }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        top: Math.random() * 100,
        delay: Math.random() * 2,
        duration: 6 + Math.random() * 8,
        size: 2 + Math.random() * 4,
      })),
    [],
  )

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <motion.div
        initial={{ opacity: 0.4 }}
        animate={{ opacity: [0.35, 0.55, 0.35] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -left-40 -top-40 h-[32rem] w-[32rem] rounded-full bg-blueGlow/20 blur-3xl"
      />
      <motion.div
        initial={{ opacity: 0.3 }}
        animate={{ opacity: [0.25, 0.45, 0.25] }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -right-32 top-24 h-[28rem] w-[28rem] rounded-full bg-violetGlow/20 blur-3xl"
      />

      <div className="grid-overlay absolute inset-0 opacity-35" />

      {particles.map((dot) => (
        <motion.span
          key={dot.id}
          initial={{ y: 0, opacity: 0.12 }}
          animate={{ y: [-10, 10, -10], opacity: [0.15, 0.65, 0.15] }}
          transition={{
            duration: dot.duration,
            delay: dot.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          style={{
            left: `${dot.left}%`,
            top: `${dot.top}%`,
            width: dot.size,
            height: dot.size,
          }}
          className="absolute rounded-full bg-cyanGlow shadow-[0_0_18px_rgba(6,247,255,0.8)]"
        />
      ))}
    </div>
  )
}
