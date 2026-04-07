import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'

import AnimatedBackground from './components/AnimatedBackground'
import Navbar from './components/Navbar'
import InputBox from './components/InputBox'
import ChatOutput from './components/ChatOutput'
import ComparisonCard from './components/ComparisonCard'
import Loader from './components/Loader'
import WhySolutionPanel from './components/WhySolutionPanel'
import { compareProblem } from './api/client'

const starterPrompt =
  'We need to choose delivery routes under fuel budget 20. Route Alpha value 14 weight 7, Route Beta value 11 weight 6, Route Gamma value 9 weight 4, Route Delta value 7 weight 3, Route Epsilon value 20 weight 11. Maximize value while respecting constraints.'

function HeroStats({ data }) {
  const cards = useMemo(
    () => [
      {
        label: 'Quantum Objective',
        value: data ? data.quantum.objective_value.toFixed(2) : '--',
      },
      {
        label: 'Classical Objective',
        value: data ? data.classical.objective_value.toFixed(2) : '--',
      },
      {
        label: 'Quantum Efficiency',
        value: data ? `${(data.comparison.approximation_ratio * 100).toFixed(2)}%` : '--',
      },
    ],
    [data],
  )

  return (
    <div className="grid gap-3 sm:grid-cols-3">
      {cards.map((card, idx) => (
        <motion.div
          key={card.label}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 * idx }}
          className="glass-card rounded-2xl p-4"
        >
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-100/65">{card.label}</p>
          <p className="mt-2 font-display text-2xl font-semibold neon-text">{card.value}</p>
        </motion.div>
      ))}
    </div>
  )
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  const runCompare = async (prompt) => {
    setLoading(true)
    setError('')

    try {
      const result = await compareProblem(prompt)
      setData(result)
    } catch (err) {
      setError(err.message || 'Failed to execute engine.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-ink text-white">
      <AnimatedBackground />
      <Navbar />

      <main className="relative z-10 mx-auto flex w-full max-w-7xl flex-col gap-6 px-6 pb-16 pt-8">
        <motion.section
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="rounded-3xl border border-cyan-300/20 bg-black/25 p-7 backdrop-blur-xl"
        >
          <p className="font-display text-xs uppercase tracking-[0.33em] text-cyan-100/80">Hero Dashboard</p>
          <h1 className="mt-3 max-w-4xl font-display text-4xl font-bold leading-tight text-white md:text-5xl">
            Quantum-AI Decision Engine
          </h1>
          <p className="mt-3 max-w-2xl text-cyan-50/85">
            Enter any optimization problem in natural language. The engine interprets it with OpenAI, runs Qiskit QAOA simulation,
            solves classically, and compares outcomes with explainability.
          </p>

          <div className="mt-6">
            <HeroStats data={data} />
          </div>
        </motion.section>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <InputBox onSubmit={runCompare} loading={loading} initialValue={starterPrompt} />
            {loading && <Loader />}
            {error && <div className="rounded-xl border border-red-400/25 bg-red-500/10 p-4 text-sm text-red-100">{error}</div>}
          </div>

          <div className="space-y-6">
            <ChatOutput
              interpretation={
                data?.interpretation ||
                'AI interpretation appears here with a live typing effect. Submit a prompt to see structured optimization reasoning.'
              }
              reasoning={
                data?.ai_reasoning ||
                'Reasoning and assumptions will be shown after OpenAI converts your prompt to optimization data.'
              }
              assumptions={data?.assumptions || []}
            />

            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card rounded-2xl p-5">
              <p className="font-display text-xs uppercase tracking-[0.25em] text-cyan-100/80">Parsed Problem</p>
              <p className="mt-2 text-sm text-cyan-50/90">
                {data
                  ? `${data.problem.problem_type} with ${data.problem.items.length} items, capacity ${data.problem.capacity.toFixed(2)}, objective ${data.problem.objective}.`
                  : 'No structured problem yet.'}
              </p>
              {data?.problem?.constraints?.length > 0 && (
                <p className="mt-2 text-xs text-cyan-100/70">Constraints: {data.problem.constraints.map((c) => c.description).slice(0, 2).join(' | ')}</p>
              )}
            </motion.div>
          </div>
        </section>

        {data && (
          <>
            <motion.section initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
              <ComparisonCard quantum={data.quantum} classical={data.classical} comparison={data.comparison} />
            </motion.section>

            <WhySolutionPanel
              text={data.why_this_solution}
              approximationRatio={data.comparison.approximation_ratio}
              efficiencyLabel={data.comparison.efficiency_label}
            />
          </>
        )}
      </main>
    </div>
  )
}
