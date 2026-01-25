import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.schemas import Debt
from agent.simulate import run_simulation

def _demo_debts():
    return [
        Debt(name="A", balance=1000, minimum=30, apr_percent=22.0),
        Debt(name="B", balance=2000, minimum=40, apr_percent=12.0),
        Debt(name="C", balance=500,  minimum=25, apr_percent=18.0),
    ]

def test_snowball_vs_avalanche_diff():
    ds = _demo_debts()
    snow = run_simulation(ds, monthly_extra=200, strategy="snowball", events=[])
    ava  = run_simulation(ds, monthly_extra=200, strategy="avalanche", events=[])
    assert snow.total_months > 0 and ava.total_months > 0
    assert snow.total_interest != ava.total_interest  # usually differ
