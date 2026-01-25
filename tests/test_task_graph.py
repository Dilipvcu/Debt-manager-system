import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.task_graph import build_graph, GraphState

def test_graph_outputs_tasks():
    g = build_graph()
    out = g.invoke(GraphState(goal_text="Become debt-free by 2027", availability_hours_per_week=2))
    assert out.tasks and len(out.tasks) >= 3
    # low availability should push some tasks later
    weeks = [t.suggested_week or 0 for t in out.tasks]
    assert max(weeks) >= 2
