# src/agent/task_graph.py
from __future__ import annotations
from typing import List
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from .schemas import Task
from .mentor_engine import lc_make_tasks

class GraphState(BaseModel):
    context: dict
    tasks: List[Task] = []

def _build_tasks(state: GraphState) -> GraphState:
    raw = lc_make_tasks(state.context)
    state.tasks = []
    for item in raw:
        try:
            state.tasks.append(Task(**item))
        except Exception:
            pass
    return state

def build_graph():
    g = StateGraph(GraphState)
    g.add_node("tasks", _build_tasks)
    g.set_entry_point("tasks")
    g.add_edge("tasks", END)
    return g.compile()
