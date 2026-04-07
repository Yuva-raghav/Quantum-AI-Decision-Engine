from __future__ import annotations

import json
from typing import Any

from openai import APIError, APITimeoutError, AuthenticationError, BadRequestError, OpenAI, RateLimitError

from app.config import get_settings
from app.schemas import Constraint, Item, ProblemDefinition


class InterpretationError(RuntimeError):
    pass


SYSTEM_PROMPT = (
    'You are an expert optimization problem parser. Convert natural language into strict JSON for knapsack or routing problems. '
    'Do not include any text outside JSON. Ensure all fields are valid and complete.'
)


RESPONSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'problem_type': {'type': 'string', 'enum': ['knapsack', 'routing']},
        'objective': {'type': 'string'},
        'capacity': {'type': 'number'},
        'items': {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'value': {'type': 'number'},
                    'weight': {'type': 'number'},
                },
                'required': ['name', 'value', 'weight'],
                'additionalProperties': False,
            },
        },
        'constraints': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'kind': {'type': 'string'},
                    'description': {'type': 'string'},
                    'value': {'type': ['number', 'null']},
                },
                'required': ['kind', 'description', 'value'],
                'additionalProperties': False,
            },
        },
        'interpretation': {'type': 'string'},
        'ai_reasoning': {'type': 'string'},
        'assumptions': {
            'type': 'array',
            'items': {'type': 'string'},
        },
    },
    'required': [
        'problem_type',
        'objective',
        'capacity',
        'items',
        'constraints',
        'interpretation',
        'ai_reasoning',
        'assumptions',
    ],
    'additionalProperties': False,
}


def _extract_text_response(response: Any) -> str:
    if hasattr(response, 'output_text') and response.output_text:
        return response.output_text

    chunks: list[str] = []
    for block in getattr(response, 'output', []):
        for content in getattr(block, 'content', []):
            text = getattr(content, 'text', None)
            if text:
                chunks.append(text)
    return '\n'.join(chunks).strip()


def _sanitize_items(raw_items: Any) -> list[Item]:
    if not isinstance(raw_items, list):
        raise InterpretationError('OpenAI returned invalid items format.')

    sanitized_items: list[Item] = []
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            continue

        name = str(raw_item.get('name', f'Option {index}')).strip()[:100]
        if not name:
            name = f'Option {index}'

        try:
            value = float(raw_item.get('value', 0))
            weight = float(raw_item.get('weight', 0))
        except (TypeError, ValueError):
            continue

        if value < 0 or weight <= 0:
            continue

        sanitized_items.append(
            Item(
                name=name,
                value=round(value, 4),
                weight=round(weight, 4),
            )
        )

    if not sanitized_items:
        raise InterpretationError('OpenAI returned no valid optimization items.')

    return sanitized_items


def _sanitize_constraints(raw_constraints: Any) -> list[Constraint]:
    if not isinstance(raw_constraints, list):
        return []

    constraints: list[Constraint] = []
    for raw in raw_constraints[:12]:
        if not isinstance(raw, dict):
            continue

        kind = str(raw.get('kind', 'general')).strip().lower()[:40] or 'general'
        description = str(raw.get('description', '')).strip()[:240]
        if len(description) < 3:
            continue

        value = raw.get('value')
        if value is not None:
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = None

        constraints.append(
            Constraint(
                kind=kind,
                description=description,
                value=value,
            )
        )

    return constraints


def _sanitize_payload(payload: dict[str, Any], model_name: str) -> tuple[ProblemDefinition, str, str, list[str]]:
    if not isinstance(payload, dict):
        raise InterpretationError('OpenAI returned malformed JSON payload.')

    try:
        capacity = float(payload.get('capacity'))
    except (TypeError, ValueError):
        raise InterpretationError('OpenAI did not provide a valid capacity value.')

    if capacity <= 0:
        raise InterpretationError('Capacity must be positive in interpreted problem.')

    problem_type = str(payload.get('problem_type', 'knapsack')).strip().lower()
    if problem_type not in {'knapsack', 'routing'}:
        problem_type = 'knapsack'

    objective = str(payload.get('objective', 'maximize')).strip().lower()
    if objective not in {'maximize', 'minimize'}:
        objective = 'maximize'

    items = _sanitize_items(payload.get('items'))
    constraints = _sanitize_constraints(payload.get('constraints'))

    interpretation = str(payload.get('interpretation', '')).strip()
    ai_reasoning = str(payload.get('ai_reasoning', '')).strip()

    if not interpretation:
        raise InterpretationError('OpenAI interpretation text was empty.')
    if not ai_reasoning:
        raise InterpretationError('OpenAI reasoning text was empty.')

    assumptions_raw = payload.get('assumptions', [])
    assumptions = []
    if isinstance(assumptions_raw, list):
        for assumption in assumptions_raw[:10]:
            text = str(assumption).strip()
            if text:
                assumptions.append(text[:200])

    problem = ProblemDefinition(
        problem_type=problem_type,
        objective=objective,
        capacity=round(capacity, 4),
        items=items,
        constraints=constraints,
        metadata={
            'source': 'openai',
            'model': model_name,
        },
    )

    return problem, interpretation, ai_reasoning, assumptions


def interpret_problem(prompt: str) -> tuple[ProblemDefinition, str, str, list[str]]:
    settings = get_settings()
    env_hint = ', '.join(settings.loaded_env_files) if settings.loaded_env_files else 'no project .env file loaded'

    if not settings.openai_api_key.strip():
        raise InterpretationError(
            f'OPENAI_API_KEY is missing or empty. Checked project env sources: {env_hint}.'
        )

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.responses.create(
            model=settings.openai_model,
            temperature=0.15,
            input=[
                {
                    'role': 'system',
                    'content': [{'type': 'input_text', 'text': SYSTEM_PROMPT}],
                },
                {
                    'role': 'user',
                    'content': [{'type': 'input_text', 'text': prompt}],
                },
            ],
            text={
                'format': {
                    'type': 'json_schema',
                    'name': 'optimization_problem',
                    'schema': RESPONSE_SCHEMA,
                    'strict': True,
                }
            },
        )

        raw_text = _extract_text_response(response)
        if not raw_text:
            raise InterpretationError('OpenAI returned empty response text.')

        print('Raw OpenAI response:', raw_text)

        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError:
            raise InterpretationError('Invalid JSON from OpenAI')

        return _sanitize_payload(payload, settings.openai_model)

    except InterpretationError:
        raise
    except AuthenticationError:
        raise InterpretationError(
            f'OpenAI authentication failed. Verify OPENAI_API_KEY in the active env source: {env_hint}.'
        )
    except RateLimitError:
        raise InterpretationError('OpenAI rate limit reached. Retry in a moment.')
    except (APITimeoutError, APIError) as exc:
        raise InterpretationError(f'OpenAI request failed: {exc}')
    except BadRequestError as exc:
        raise InterpretationError(f'OpenAI rejected the request: {exc}')
    except Exception as exc:
        raise InterpretationError(f'OpenAI parsing failed. Check API or input. Details: {exc}')
