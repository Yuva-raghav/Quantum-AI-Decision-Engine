from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from app.schemas import ProblemDefinition, SolverResult
from app.services.problem_utils import evaluate_bitstring, modified_quantum_objective, qiskit_key_to_bitstring


@dataclass
class IsingCoefficients:
    h: np.ndarray
    j: dict[tuple[int, int], float]


def _build_qubo_coefficients(problem: ProblemDefinition, penalty: float) -> tuple[np.ndarray, dict[tuple[int, int], float]]:
    values = np.array([item.value for item in problem.items], dtype=float)
    weights = np.array([item.weight for item in problem.items], dtype=float)
    capacity = float(problem.capacity)

    linear = -values + penalty * (weights ** 2 - 2 * capacity * weights)
    quadratic: dict[tuple[int, int], float] = {}

    for i in range(len(problem.items)):
        for j in range(i + 1, len(problem.items)):
            quadratic[(i, j)] = 2 * penalty * weights[i] * weights[j]

    return linear, quadratic


def _qubo_to_ising(linear: np.ndarray, quadratic: dict[tuple[int, int], float]) -> IsingCoefficients:
    n = len(linear)
    h = np.zeros(n, dtype=float)
    j_coeffs: dict[tuple[int, int], float] = {}

    for i in range(n):
        h[i] += -0.5 * linear[i]

    for (i, k), coeff in quadratic.items():
        h[i] += -0.25 * coeff
        h[k] += -0.25 * coeff
        j_coeffs[(i, k)] = 0.25 * coeff

    return IsingCoefficients(h=h, j=j_coeffs)


def _build_qaoa_circuit(n: int, gamma: float, beta: float, ising: IsingCoefficients) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    qc.h(range(n))

    for i in range(n):
        coeff = ising.h[i]
        if abs(coeff) > 1e-10:
            qc.rz(2 * gamma * coeff, i)

    for (i, j), coeff in ising.j.items():
        if abs(coeff) > 1e-10:
            qc.rzz(2 * gamma * coeff, i, j)

    for i in range(n):
        qc.rx(2 * beta, i)

    qc.measure(range(n), range(n))
    return qc


def _expected_modified_score(problem: ProblemDefinition, counts: dict[str, int], penalty: float) -> float:
    shots = max(1, sum(counts.values()))
    total = 0.0
    for raw_key, count in counts.items():
        bitstring = qiskit_key_to_bitstring(raw_key, len(problem.items))
        score = modified_quantum_objective(problem, bitstring, penalty)
        total += score * count
    return total / shots


def _sample_feasible_solution(problem: ProblemDefinition, counts: dict[str, int], rng: np.random.Generator):
    feasible_rows = []
    for raw_key, count in counts.items():
        bitstring = qiskit_key_to_bitstring(raw_key, len(problem.items))
        evaluated = evaluate_bitstring(problem, bitstring)
        if evaluated.feasible:
            feasible_rows.append((evaluated, count))

    if feasible_rows:
        # Temperature (<1) flattens distribution, preserving probabilistic behavior and avoiding always-optimal picks.
        raw = np.array([row[1] for row in feasible_rows], dtype=float)
        probs = np.power(raw, 0.72)
        probs = probs / probs.sum()

        sampled_index = int(rng.choice(len(feasible_rows), p=probs))
        sampled_eval, sampled_count = feasible_rows[sampled_index]

        best_feasible = max(feasible_rows, key=lambda row: row[0].objective_value)[0]
        return sampled_eval, sampled_count, float(probs[sampled_index]), best_feasible

    # Fallback if all sampled states violate constraints.
    fallback_eval = None
    fallback_count = 0
    for raw_key, count in counts.items():
        bitstring = qiskit_key_to_bitstring(raw_key, len(problem.items))
        evaluated = evaluate_bitstring(problem, bitstring)
        if fallback_eval is None or evaluated.objective_value > fallback_eval.objective_value:
            fallback_eval = evaluated
            fallback_count = count

    return fallback_eval, fallback_count, 0.0, fallback_eval


def solve_quantum(problem: ProblemDefinition, shots: int = 1024) -> SolverResult:
    start = time.perf_counter()

    n = len(problem.items)
    seed = int(time.time_ns() % 2_147_483_647)
    rng = np.random.default_rng(seed)
    simulator = AerSimulator(seed_simulator=seed)

    penalty = max(item.value for item in problem.items) + 1.0
    linear, quadratic = _build_qubo_coefficients(problem, penalty)
    ising = _qubo_to_ising(linear, quadratic)

    gamma_values = np.linspace(0.05, math.pi, 8)
    beta_values = np.linspace(0.05, math.pi / 2, 8)

    best_params = (gamma_values[0], beta_values[0])
    best_score = -float('inf')

    for gamma in gamma_values:
        for beta in beta_values:
            circuit = _build_qaoa_circuit(n, float(gamma), float(beta), ising)
            transpiled = transpile(circuit, simulator)
            counts = simulator.run(transpiled, shots=min(shots, 512)).result().get_counts()
            expected = _expected_modified_score(problem, counts, penalty)
            if expected > best_score:
                best_score = expected
                best_params = (float(gamma), float(beta))

    final_circuit = _build_qaoa_circuit(n, best_params[0], best_params[1], ising)
    final_counts = simulator.run(transpile(final_circuit, simulator), shots=shots).result().get_counts()

    sampled_eval, sampled_count, sampled_probability, best_feasible = _sample_feasible_solution(problem, final_counts, rng)

    elapsed_ms = (time.perf_counter() - start) * 1000

    return SolverResult(
        method='quantum',
        objective_value=sampled_eval.objective_value,
        total_weight=sampled_eval.total_weight,
        feasible=sampled_eval.feasible,
        selected_items=sampled_eval.selected_items,
        bitstring=sampled_eval.bitstring,
        runtime_ms=round(elapsed_ms, 3),
        diagnostics={
            'shots': shots,
            'seed': seed,
            'best_params': {'gamma': round(best_params[0], 4), 'beta': round(best_params[1], 4)},
            'best_expected_modified_score': round(best_score, 4),
            'sampled_solution_probability': round(sampled_probability, 4),
            'best_feasible_objective_in_distribution': round(best_feasible.objective_value, 4),
            'sampled_states': len(final_counts),
            'preview_counts': dict(sorted(final_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'note': 'Quantum result is a probabilistic QAOA sample and may vary between runs.',
            'selected_measurement_count': int(sampled_count),
        },
    )
