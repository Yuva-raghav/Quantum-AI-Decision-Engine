import { motion } from 'framer-motion'
import { BadgeCheck, CircleHelp, Clock3, Cpu, Trophy, Weight } from 'lucide-react'

function StatPill({ icon: Icon, label, value }) {
  return (
    <div className="rounded-xl border border-cyan-200/15 bg-black/25 px-3 py-2">
      <p className="inline-flex items-center gap-1 text-[11px] uppercase tracking-[0.14em] text-cyan-100/70">
        <Icon size={12} />
        {label}
      </p>
      <p className="mt-1 text-sm font-semibold text-white">{value}</p>
    </div>
  )
}

function Badge({ text, colorClass }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] ${colorClass}`}>
      {text}
    </span>
  )
}

function ResultCard({ title, subtitle, result, glowClass, badgeText, badgeClass, showTooltip }) {
  return (
    <motion.article whileHover={{ y: -4 }} className={`glass-card rounded-2xl p-5 ${glowClass}`}>
      <div className="flex items-center justify-between gap-3">
        <p className="font-display text-xs uppercase tracking-[0.24em] text-cyan-100/70">{subtitle}</p>
        <Badge text={badgeText} colorClass={badgeClass} />
      </div>

      <div className="mt-1 flex items-center gap-2">
        <h3 className="font-display text-2xl font-semibold text-white">{title}</h3>
        {showTooltip && (
          <span
            title="QAOA (Quantum Approximate Optimization Algorithm) samples probabilistic solutions from a quantum circuit."
            className="inline-flex cursor-help text-cyan-100/75"
          >
            <CircleHelp size={16} />
          </span>
        )}
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2">
        <StatPill icon={Trophy} label="Objective" value={result.objective_value.toFixed(2)} />
        <StatPill icon={Weight} label="Weight" value={result.total_weight.toFixed(2)} />
        <StatPill icon={Clock3} label="Runtime" value={`${result.runtime_ms.toFixed(2)} ms`} />
      </div>

      <div className="mt-4 rounded-xl border border-cyan-300/15 bg-black/25 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-cyan-100/70">Selected Items</p>
        <p className="mt-2 text-sm text-white/90">
          {result.selected_items.length > 0 ? result.selected_items.join(', ') : 'No item selected'}
        </p>
        <p className="mt-2 text-xs text-cyan-100/65">Bitstring: {result.bitstring}</p>
      </div>

      {result.method === 'quantum' && (
        <p className="mt-3 text-xs text-cyan-100/75">Result may vary due to probabilistic nature.</p>
      )}
    </motion.article>
  )
}

function efficiencyClasses(color) {
  if (color === 'green') return 'border-emerald-300/40 bg-emerald-300/15 text-emerald-100'
  if (color === 'yellow') return 'border-amber-300/40 bg-amber-300/15 text-amber-100'
  return 'border-rose-300/40 bg-rose-300/15 text-rose-100'
}

export default function ComparisonCard({ quantum, classical, comparison }) {
  const objectiveMax = Math.max(quantum.objective_value, classical.objective_value, 1)
  const runtimeMax = Math.max(quantum.runtime_ms, classical.runtime_ms, 1)
  const ratioPercent = (comparison.approximation_ratio * 100).toFixed(2)

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-2">
        <ResultCard
          title="Quantum Approximation"
          subtitle="QAOA Simulation"
          result={quantum}
          glowClass="shadow-neon"
          badgeText="Quantum Simulation"
          badgeClass="border-cyan-300/45 bg-cyan-300/15 text-cyan-100"
          showTooltip
        />
        <ResultCard
          title="Classical Solver"
          subtitle="Exact Benchmark"
          result={classical}
          glowClass="shadow-violet"
          badgeText="Classical Optimal"
          badgeClass="border-violet-300/40 bg-violet-300/15 text-violet-100"
        />
      </div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card rounded-2xl p-5">
        <p className="font-display text-xs uppercase tracking-[0.25em] text-cyan-100/80">Performance Comparison</p>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1 rounded-full border border-cyan-200/20 bg-black/30 px-3 py-1 text-xs text-cyan-100/85">
            <Cpu size={12} />
            Quantum Efficiency: {ratioPercent}%
          </span>
          <span className="inline-flex items-center gap-1 rounded-full border border-violet-200/20 bg-black/30 px-3 py-1 text-xs text-violet-100/85">
            <BadgeCheck size={12} />
            Classical Optimal
          </span>
          <span className={`inline-flex rounded-full border px-3 py-1 text-xs ${efficiencyClasses(comparison.efficiency_color)}`}>
            {comparison.efficiency_label} closeness
          </span>
        </div>

        <div className="mt-5 space-y-4">
          <div>
            <div className="mb-2 flex justify-between text-xs text-cyan-100/75">
              <span>Objective Score</span>
              <span>Quantum vs Classical</span>
            </div>
            <div className="space-y-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(quantum.objective_value / objectiveMax) * 100}%` }}
                transition={{ duration: 0.8 }}
                className="h-2 rounded-full bg-gradient-to-r from-cyanGlow to-blueGlow"
              />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(classical.objective_value / objectiveMax) * 100}%` }}
                transition={{ duration: 0.8, delay: 0.1 }}
                className="h-2 rounded-full bg-gradient-to-r from-violetGlow to-blueGlow"
              />
            </div>
          </div>

          <div>
            <div className="mb-2 flex justify-between text-xs text-cyan-100/75">
              <span>Runtime (lower is better)</span>
              <span>ms scale</span>
            </div>
            <div className="space-y-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(quantum.runtime_ms / runtimeMax) * 100}%` }}
                transition={{ duration: 0.8 }}
                className="h-2 rounded-full bg-cyan-300/85"
              />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(classical.runtime_ms / runtimeMax) * 100}%` }}
                transition={{ duration: 0.8, delay: 0.1 }}
                className="h-2 rounded-full bg-violet-300/85"
              />
            </div>
          </div>
        </div>

        <div className="mt-5 rounded-xl border border-cyan-200/15 bg-black/25 p-3 text-sm text-cyan-50/90">{comparison.summary}</div>
      </motion.div>
    </div>
  )
}
