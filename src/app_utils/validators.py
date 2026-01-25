# src/app_utils/validators.py
from __future__ import annotations
from typing import List
# ✅ Use absolute import (works when running "streamlit run src/app.py")
from agent.schemas import Debt

def dollars(x: float) -> str:
    return f"${x:,.2f}"

def validate_debts(debts: List[Debt]) -> List[str]:
    errs = []
    if not debts:
        errs.append("Please add at least one debt.")
        return errs
    for d in debts:
        if d.balance < 0:
            errs.append(f"[{d.name}] Balance cannot be negative.")
        if d.minimum < 0:
            errs.append(f"[{d.name}] Minimum cannot be negative.")
        if d.apr_percent < 0 or d.apr_percent > 100:
            errs.append(f"[{d.name}] APR must be between 0 and 100.")
    if sum(d.minimum for d in debts) == 0:
        errs.append("At least one debt should have a positive minimum payment.")
    return errs
