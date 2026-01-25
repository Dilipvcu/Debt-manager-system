from typing import List
from .schemas import Debt, StrategyType

__all__ = ["order_debts"]

def order_debts(debts: List[Debt], strategy: StrategyType) -> List[int]:
    """
    Return indices of debts in the order they should be paid.

    - Snowball  : smallest balance first (stable tiebreak on original index)
    - Avalanche : highest APR first     (stable tiebreak on original index)
    """
    indexed = list(enumerate(debts))
    if strategy == "snowball":
        indexed.sort(key=lambda it: (it[1].balance, it[0]))
    else:  # avalanche
        indexed.sort(key=lambda it: (-it[1].apr_percent, it[0]))
    return [i for i, _ in indexed]
