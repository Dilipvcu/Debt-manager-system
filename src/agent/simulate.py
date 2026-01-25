# src/agent/simulate.py
from __future__ import annotations
from typing import List, Tuple
from dataclasses import dataclass, field
import pandas as pd
from .schemas import Debt, StrategyType, AppEvent

@dataclass
class SimulationResult:
    total_months: int
    total_interest: float
    payoff_months_by_debt: List[Tuple[str, int]]  # [(debt_name, month_finished)]
    per_debt_interest: List[Tuple[str, float]]
    _summary_df: pd.DataFrame = field(repr=False, default_factory=pd.DataFrame)

    def payoff_table(self) -> pd.DataFrame:
        if not self._summary_df.empty:
            return self._summary_df.copy()
        rows = []
        for (name, m), (_, intr) in zip(self.payoff_months_by_debt, self.per_debt_interest):
            rows.append({"Debt": name, "Months_to_Payoff": m, "Interest_Paid": round(intr, 2)})
        return pd.DataFrame(rows)

    def debt_free_date(self, start_date) -> "date":
        from datetime import timedelta
        months = self.total_months
        # approximate: 30 days per month
        return start_date + timedelta(days=30*months)

    def to_csv(self) -> str:
        return self.payoff_table().to_csv(index=False)

def run_simulation(
    debts: List[Debt],
    monthly_extra: float,
    strategy: StrategyType,
    events: List[AppEvent],
) -> SimulationResult:
    assert strategy == "avalanche", "Only avalanche supported in this build."

    # Clone balances
    balances = {d.name: float(d.balance) for d in debts}
    aprs = {d.name: float(d.apr_percent) for d in debts}
    mins = {d.name: float(d.minimum) for d in debts}

    month_finished = {d.name: None for d in debts}
    interest_by_debt = {d.name: 0.0 for d in debts}

    months = 0
    total_interest = 0.0

    def all_clear() -> bool:
        return all(balances[n] <= 0.000001 for n in balances)

    # events are one-shot per call; we apply at the first month
    pending_bonus = 0.0
    missed_only_mins = False
    for e in events:
        if e.kind == "bonus":
            amt = float(e.payload.get("amount", 0.0))
            if amt > 0:
                pending_bonus += amt
        elif e.kind == "missed_payment":
            missed_only_mins = True

    # Guard against zero-pay loops
    hard_cap = 600

    while not all_clear() and months < hard_cap:
        months += 1
        # 1) accrue interest
        month_interest_total = 0.0
        for name, bal in balances.items():
            if bal <= 0:
                continue
            r = (aprs[name] / 100.0) / 12.0
            intr = bal * r
            balances[name] += intr
            interest_by_debt[name] += intr
            month_interest_total += intr
        total_interest += month_interest_total

        # 2) pay minimums
        pay_pool = 0.0
        for name in balances:
            if balances[name] <= 0:
                continue
            p = min(mins[name], balances[name])
            balances[name] -= p
        # 3) add extra
        extra = 0.0 if missed_only_mins else max(0.0, float(monthly_extra))
        # bonus applies once (first month)
        if pending_bonus > 0:
            extra += pending_bonus
            pending_bonus = 0.0

        # 4) avalanche extra -> highest APR first, then next, etc.
        # order debts by APR desc, then balance desc
        order = sorted([n for n in balances.keys() if balances[n] > 0],
                       key=lambda n: (aprs[n], balances[n]), reverse=True)
        for name in order:
            if extra <= 0:
                break
            pay = min(extra, balances[name])
            balances[name] -= pay
            extra -= pay

        # 5) mark finished
        for name in balances:
            if balances[name] <= 0 and month_finished[name] is None:
                month_finished[name] = months

        # Loop escape if truly no progress (all minimums are zero and no extra)
        if month_interest_total == 0 and all(mins[n] == 0 for n in balances) and (monthly_extra <= 0) and not events:
            break

    payoff_pairs = [(n, month_finished[n] or months) for n in balances]
    per_debt_intr = [(n, interest_by_debt[n]) for n in balances]
    # summary per debt
    rows = []
    for n in balances:
        rows.append({
            "Debt": n,
            "Months_to_Payoff": month_finished[n] or months,
            "Interest_Paid": round(interest_by_debt[n], 2),
        })
    df = pd.DataFrame(rows, columns=["Debt", "Months_to_Payoff", "Interest_Paid"])
    return SimulationResult(
        total_months=months,
        total_interest=round(total_interest, 2),
        payoff_months_by_debt=payoff_pairs,
        per_debt_interest=per_debt_intr,
        _summary_df=df,
    )
