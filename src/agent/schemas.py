# src/agent/schemas.py
from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

StrategyType = Literal["avalanche"]

class Debt(BaseModel):
    name: str = Field(..., min_length=1)
    balance: float = Field(..., ge=0.0)
    minimum: float = Field(..., ge=0.0)
    apr_percent: float = Field(..., ge=0.0, le=100.0)

    @field_validator("balance", "minimum", "apr_percent")
    @classmethod
    def _round2(cls, v: float) -> float:
        return float(round(v, 4))

class UserInput(BaseModel):
    debts: List[Debt]
    strategy: StrategyType
    monthly_extra: float = Field(ge=0.0, default=0.0)

class AppEvent(BaseModel):
    kind: Literal["bonus", "missed_payment"]
    payload: dict = Field(default_factory=dict)

class Task(BaseModel):
    id: str
    title: str
    description: str
    suggested_week: Optional[int] = None
    done: bool = False
