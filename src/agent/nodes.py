from typing import Dict, Any
from .schemas import Plan, Task, AppEvent, UserInput

BASE_TASKS = [
    ("Enter debts", "Provide Name, Balance, Min, APR for each debt"),
    ("Choose strategy", "Pick Snowball or Avalanche"),
    ("Set extra budget", "Choose monthly extra you can afford"),
    ("Run simulation", "Compute payoff months & interest"),
    ("Apply events", "Add bonus or mark missed payment when needed"),
    ("Rollover when paid", "When a debt hits $0, roll its payment to next focus"),
]

def node_plan_request(state: Dict[str, Any]) -> Dict[str, Any]:
    event = state.get("event") or {}
    payload = event.get("payload") or {}
    _ = UserInput(**payload)  # validate structure
    tasks = [Task(title=t, description=d) for t, d in BASE_TASKS]
    plan = Plan(tasks=tasks, next_action=tasks[0].title)
    return {"plan": plan}

def node_adapt(state: Dict[str, Any]) -> Dict[str, Any]:
    plan = Plan(**state.get("plan", {}))
    event = state.get("event") or {}
    evt = AppEvent(**event)
    if evt.kind == "task_done":
        tid = evt.payload.get("task_id")
        for t in plan.tasks:
            if t.id == tid:
                t.status = "done"
        plan.next_action = next((t.title for t in plan.tasks if t.status != "done"), "All tasks complete")
    elif evt.kind in {"bonus", "missed_payment"}:
        plan.next_action = "Re-run simulation with latest events"
    return {"plan": plan}
