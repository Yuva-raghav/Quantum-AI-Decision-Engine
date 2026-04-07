from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from pydantic import BaseModel, Field


load_dotenv()


def _candidate_env_files() -> list[Path]:
    backend_root = Path(__file__).resolve().parents[1]
    return [
        backend_root / ".env",
        backend_root / "app" / "services" / ".env",
    ]


def _load_settings_map() -> tuple[dict[str, str], list[str]]:
    resolved: dict[str, str] = dict(os.environ)
    loaded_files: list[str] = []

    # Project-local env files should win over any stale shell environment.
    for env_path in reversed(_candidate_env_files()):
        if env_path.exists():
            values = {
                key: value
                for key, value in dotenv_values(env_path).items()
                if value is not None
            }
            resolved.update(values)
            loaded_files.append(str(env_path))

    loaded_files.reverse()
    return resolved, loaded_files


class Settings(BaseModel):
    app_name: str = "Quantum-AI Decision Engine API"
    app_version: str = "1.0.0"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    qbraid_api_key: str = ""
    loaded_env_files: list[str] = Field(default_factory=list)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    values, loaded_files = _load_settings_map()
    return Settings(
        openai_api_key=values.get("OPENAI_API_KEY", ""),
        openai_model=values.get("OPENAI_MODEL", "gpt-4o-mini"),
        qbraid_api_key=values.get("QBRAID_API_KEY", ""),
        loaded_env_files=loaded_files,
    )
