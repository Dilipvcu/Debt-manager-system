# src/agent/mentor_engine.py
from __future__ import annotations
import os, json

from langchain_openai import ChatOpenAI  # type: ignore

def _llm() -> ChatOpenAI:
    api = os.getenv("OPENAI_API_KEY", "").strip()
    if not api:
        raise RuntimeError("OPENAI_API_KEY missing. Add it to your .env.")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0.3, openai_api_key=api)

def lc_explain_strategy_avalanche() -> str:
    llm = _llm()
    msg = [
        ("system", "Explain briefly for a finance class."),
        ("user", "In ≤45 words, explain Avalanche debt payoff and why it minimizes interest."),
    ]
    return (llm.invoke(msg).content or "").strip()

def lc_next_actions(context: dict) -> str:
    llm = _llm()
    prompt = [
        ("system",
         "You are a concise, practical debt mentor. "
         "Return 4–6 short, personalized bullets. No fluff. Mention concrete amounts/dates if provided."),
        ("user", f"User situation as JSON:\n{json.dumps(context, ensure_ascii=False)}")
    ]
    return (llm.invoke(prompt).content or "").strip()

def lc_make_tasks(context: dict) -> list[dict]:
    """
    Return JSON array of 4–6 task dicts: {id, title, description, suggested_week, done}
    Keep tasks 30–60 minutes each. Be concrete (names, amounts, dates) if present in context.
    """
    llm = _llm()
    prompt = [
        ("system",
         "You are a finance mentor. Output ONLY JSON array with tasks: "
         "id, title, description, suggested_week (int), done (bool). No markdown, no prose—JSON only."),
        ("user", json.dumps(context, ensure_ascii=False))
    ]
    txt = (llm.invoke(prompt).content or "").strip()
    return json.loads(txt)
