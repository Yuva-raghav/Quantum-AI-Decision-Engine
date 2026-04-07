from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import CompareRequest, CompareResponse, InterpretResponse, PromptRequest, SolveRequest, SolverResult
from app.services.ai_interpreter import InterpretationError, interpret_problem
from app.services.classical_solver import solve_classically
from app.services.comparator import build_why_solution, compare_solutions
from app.services.problem_utils import normalize_problem
from app.services.quantum_solver import solve_quantum

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health() -> dict:
    return {
        'status': 'ok',
        'service': settings.app_name,
        'version': settings.app_version,
        'openai_configured': bool(settings.openai_api_key.strip()),
        'loaded_env_files': settings.loaded_env_files,
    }


@app.post('/interpret', response_model=InterpretResponse)
def interpret(req: PromptRequest) -> InterpretResponse:
    try:
        problem, interpretation, ai_reasoning, assumptions = interpret_problem(req.message)
        problem = normalize_problem(problem)
        return InterpretResponse(
            problem=problem,
            interpretation=interpretation,
            ai_reasoning=ai_reasoning,
            assumptions=assumptions,
        )
    except InterpretationError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post('/solve-quantum', response_model=SolverResult)
def solve_quantum_route(payload: SolveRequest) -> SolverResult:
    try:
        problem = normalize_problem(payload.problem)
        return solve_quantum(problem)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post('/solve-classical', response_model=SolverResult)
def solve_classical_route(payload: SolveRequest) -> SolverResult:
    try:
        problem = normalize_problem(payload.problem)
        return solve_classically(problem)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post('/compare', response_model=CompareResponse)
def compare(payload: CompareRequest) -> CompareResponse:
    try:
        if payload.problem:
            problem = normalize_problem(payload.problem)
            interpretation = 'Using provided structured optimization problem.'
            ai_reasoning = 'Structured data was provided directly, so parser inference was skipped.'
            assumptions = []
        else:
            problem, interpretation, ai_reasoning, assumptions = interpret_problem(payload.message or '')
            problem = normalize_problem(problem)

        quantum_result = solve_quantum(problem)
        classical_result = solve_classically(problem)
        comparison = compare_solutions(problem, quantum_result, classical_result)
        why_this_solution = build_why_solution(problem, quantum_result, classical_result, comparison)

        return CompareResponse(
            problem=problem,
            interpretation=interpretation,
            ai_reasoning=ai_reasoning,
            assumptions=assumptions,
            quantum=quantum_result,
            classical=classical_result,
            comparison=comparison,
            why_this_solution=why_this_solution,
        )
    except InterpretationError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
