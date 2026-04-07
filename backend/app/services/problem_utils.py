from __future__ import annotations

from dataclasses import dataclass

from app.schemas import Constraint, ProblemDefinition


@dataclass
class EvaluatedSolution:
    objective_value: float
    total_weight: float
    feasible: bool
    selected_items: list[str]
    bitstring: str


def normalize_problem(problem: ProblemDefinition) -> ProblemDefinition:
    if problem.capacity <= 0:
        raise ValueError('Capacity must be positive.')

    if problem.objective != 'maximize':
        raise ValueError("Current solvers support only 'maximize' objective problems.")

    if not problem.constraints:
        problem.constraints = [
            Constraint(
                kind='capacity',
                description='Total selected weight cannot exceed capacity.',
                value=problem.capacity,
            )
        ]

    if len(problem.items) > 10:
        ranked = sorted(
            problem.items,
            key=lambda x: (x.value / x.weight) if x.weight else x.value,
            reverse=True,
        )
        problem.items = ranked[:10]
        problem.metadata['truncated_items'] = True
        problem.metadata['truncated_to'] = 10

    return problem


def evaluate_bitstring(problem: ProblemDefinition, bitstring: str) -> EvaluatedSolution:
    if len(bitstring) != len(problem.items):
        raise ValueError('Bitstring length must match item count.')

    selected = []
    total_value = 0.0
    total_weight = 0.0

    for bit, item in zip(bitstring, problem.items):
        if bit == '1':
            selected.append(item.name)
            total_value += item.value
            total_weight += item.weight

    return EvaluatedSolution(
        objective_value=round(total_value, 4),
        total_weight=round(total_weight, 4),
        feasible=total_weight <= problem.capacity,
        selected_items=selected,
        bitstring=bitstring,
    )


def modified_quantum_objective(problem: ProblemDefinition, bitstring: str, penalty: float) -> float:
    evaluated = evaluate_bitstring(problem, bitstring)
    overflow = max(0.0, evaluated.total_weight - problem.capacity)
    return evaluated.objective_value - penalty * (overflow ** 2)


def qiskit_key_to_bitstring(key: str, num_bits: int) -> str:
    compact = key.replace(' ', '')
    padded = compact.rjust(num_bits, '0')
    return padded[::-1]
