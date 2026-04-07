from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float = Field(..., ge=0)
    weight: float = Field(..., gt=0)


class Constraint(BaseModel):
    kind: str = Field(..., min_length=1, max_length=40)
    description: str = Field(..., min_length=3, max_length=240)
    value: float | None = None


class ProblemDefinition(BaseModel):
    problem_type: Literal['knapsack', 'routing'] = 'knapsack'
    objective: str = 'maximize'
    capacity: float = Field(..., gt=0)
    items: list[Item] = Field(..., min_length=1)
    constraints: list[Constraint] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptRequest(BaseModel):
    message: str | None = Field(default=None, min_length=10, max_length=4000)
    prompt: str | None = Field(default=None, min_length=10, max_length=4000)

    @model_validator(mode='after')
    def normalize_message(self) -> 'PromptRequest':
        if not self.message and self.prompt:
            self.message = self.prompt
        if not self.message:
            raise ValueError('message is required.')
        return self


class InterpretResponse(BaseModel):
    problem: ProblemDefinition
    interpretation: str
    ai_reasoning: str
    assumptions: list[str] = Field(default_factory=list)


class SolveRequest(BaseModel):
    problem: ProblemDefinition


class SolverResult(BaseModel):
    method: Literal['quantum', 'classical']
    objective_value: float
    total_weight: float
    feasible: bool
    selected_items: list[str]
    bitstring: str
    runtime_ms: float
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    message: str | None = None
    prompt: str | None = None
    problem: ProblemDefinition | None = None

    @model_validator(mode='after')
    def validate_input(self) -> 'CompareRequest':
        if not self.message and self.prompt:
            self.message = self.prompt
        if not self.message and not self.problem:
            raise ValueError('Either message or problem must be provided.')
        return self


class ComparisonResult(BaseModel):
    winner: Literal['quantum', 'classical']
    value_gap: float
    quantum_vs_classical_percent: float
    approximation_ratio: float
    efficiency_label: Literal['High', 'Moderate', 'Low']
    efficiency_color: Literal['green', 'yellow', 'red']
    runtime_ratio_classical_over_quantum: float
    summary: str


class CompareResponse(BaseModel):
    problem: ProblemDefinition
    interpretation: str
    ai_reasoning: str
    assumptions: list[str] = Field(default_factory=list)
    quantum: SolverResult
    classical: SolverResult
    comparison: ComparisonResult
    why_this_solution: str
