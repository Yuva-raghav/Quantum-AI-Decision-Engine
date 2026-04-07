from __future__ import annotations

import itertools
import time

from app.schemas import ProblemDefinition, SolverResult
from app.services.problem_utils import evaluate_bitstring


def solve_classically(problem: ProblemDefinition) -> SolverResult:
    start = time.perf_counter()

    num_items = len(problem.items)
    best = None

    for bits in itertools.product('01', repeat=num_items):
        bitstring = ''.join(bits)
        evaluated = evaluate_bitstring(problem, bitstring)
        if not evaluated.feasible:
            continue

        if best is None or evaluated.objective_value > best.objective_value:
            best = evaluated

    if best is None:
        best = evaluate_bitstring(problem, '0' * num_items)

    elapsed_ms = (time.perf_counter() - start) * 1000

    return SolverResult(
        method='classical',
        objective_value=best.objective_value,
        total_weight=best.total_weight,
        feasible=best.feasible,
        selected_items=best.selected_items,
        bitstring=best.bitstring,
        runtime_ms=round(elapsed_ms, 3),
        diagnostics={
            'search_space_size': 2 ** num_items,
        },
    )
