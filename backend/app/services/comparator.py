from __future__ import annotations

from app.schemas import ComparisonResult, ProblemDefinition, SolverResult


def _efficiency_band(approximation_ratio: float) -> tuple[str, str]:
    if approximation_ratio >= 0.9:
        return 'High', 'green'
    if approximation_ratio >= 0.75:
        return 'Moderate', 'yellow'
    return 'Low', 'red'


def compare_solutions(problem: ProblemDefinition, quantum: SolverResult, classical: SolverResult) -> ComparisonResult:
    value_gap = classical.objective_value - quantum.objective_value
    approximation_ratio = (
        quantum.objective_value / classical.objective_value
        if classical.objective_value > 0
        else 0.0
    )

    pct_of_optimum = approximation_ratio * 100

    runtime_ratio = (
        classical.runtime_ms / quantum.runtime_ms
        if quantum.runtime_ms > 0
        else 0.0
    )

    winner = 'classical' if classical.objective_value >= quantum.objective_value else 'quantum'
    efficiency_label, efficiency_color = _efficiency_band(approximation_ratio)

    return ComparisonResult(
        winner=winner,
        value_gap=round(value_gap, 4),
        quantum_vs_classical_percent=round(pct_of_optimum, 2),
        approximation_ratio=round(approximation_ratio, 4),
        efficiency_label=efficiency_label,
        efficiency_color=efficiency_color,
        runtime_ratio_classical_over_quantum=round(runtime_ratio, 3),
        summary=(
            f"Quantum Approximation (QAOA Simulation) reached {pct_of_optimum:.2f}% of the classical optimal score. "
            f"Objective gap is {value_gap:.4f}."
        ),
    )


def build_why_solution(problem: ProblemDefinition, quantum: SolverResult, classical: SolverResult, comparison: ComparisonResult) -> str:
    quantum_items = ', '.join(quantum.selected_items) if quantum.selected_items else 'no items'
    classical_items = ', '.join(classical.selected_items) if classical.selected_items else 'no items'

    constraint_clause = (
        '; '.join(c.description for c in problem.constraints[:3])
        if problem.constraints
        else f'capacity limit {problem.capacity:.2f}'
    )

    return (
        f"Quantum selected {quantum_items} (weight {quantum.total_weight:.2f}) while classical optimal selected {classical_items} "
        f"(weight {classical.total_weight:.2f}). Decisions were constrained by {constraint_clause}. "
        f"Because QAOA is probabilistic, the quantum run targeted a high-quality feasible bitstring rather than guaranteed optimum. "
        f"Current quantum efficiency is {comparison.quantum_vs_classical_percent:.2f}% ({comparison.efficiency_label})."
    )
