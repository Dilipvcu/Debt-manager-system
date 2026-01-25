# src/app.py
import sys
import os
import json
import hashlib
from typing import List
from datetime import datetime, date
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

#login   modules addition

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv()

from agent.schemas import Debt, UserInput, AppEvent, Task
from agent.simulate import run_simulation
from agent.task_graph import build_graph, GraphState
from agent.mentor_engine import lc_explain_strategy_avalanche, lc_next_actions
from app_utils.validators import validate_debts, dollars
from app_utils.store import load_state, save_state

STRATEGY = "avalanche"  # keep it simple & optimal

# ---------- auth helpers ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_users():
    app_data_dir = os.path.expanduser('~/.debt_planner')
    users_file = os.path.join(app_data_dir, 'users.json')
    try:
        with open(users_file, 'w') as f:
            json.dump(st.session_state['users'], f)
    except IOError as e:
        st.error(f"Unable to save user data: {str(e)}")
        return False
    return True

# ---------- helpers ----------
def sum_minimums(debts: List[Debt]) -> float:
    return float(sum(d.minimum for d in debts))

def safe_extra_from_budget(net_income: float, fixed_bills: float, essentials: float, buffer_amt: float, debts: List[Debt]) -> float:
    leftover = net_income - fixed_bills - essentials - sum_minimums(debts) - buffer_amt
    return max(0.0, round(leftover, 2))

def required_extra_for_months(debts: List[Debt], months: int) -> float:
    lo, hi = 0.0, max(100.0, sum(float(d.balance) for d in debts))
    best = None
    for _ in range(40):
        mid = (lo + hi) / 2.0
        sim = run_simulation(debts, mid, STRATEGY, [])
        if sim.total_months <= months:
            best, hi = mid, mid
        else:
            lo = mid
    return round(best if best is not None else hi, 2)

def classify_status(net_income: float, fixed_bills: float, essentials: float, debts: List[Debt]) -> str:
    must = fixed_bills + essentials + sum_minimums(debts)
    if net_income <= 0 or net_income < must:
        return "zero_income"
    return "ok"

# Initialize authentication state
app_data_dir = os.path.expanduser('~/.debt_planner')
if not os.path.exists(app_data_dir):
    try:
        os.makedirs(app_data_dir)
    except OSError as e:
        st.error(f"Unable to create app data directory: {str(e)}")

users_file = os.path.join(app_data_dir, 'users.json')
if 'users' not in st.session_state:
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                st.session_state['users'] = json.load(f)
        except IOError as e:
            st.error(f"Unable to read user data: {str(e)}")
            st.session_state['users'] = {}
    else:
        st.session_state['users'] = {}

# Initialize login state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# Initialize other state
persist = load_state()
if "events" not in st.session_state: st.session_state["events"] = []
if "history" not in st.session_state: st.session_state["history"] = persist.get("history", [])
if "tasks" not in st.session_state: st.session_state["tasks"] = [Task(**t) for t in persist.get("tasks", [])] if persist.get("tasks") else []

# ---------- UI ----------
st.set_page_config(page_title="Debt Mentor (Avalanche)", layout="wide")

# Apply custom styling
st.markdown("""
    <style>
        .main { padding: 2rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
        .stTabs [data-baseweb="tab"] { padding: 1rem 2rem; }
        .welcome-box { 
            padding: 2rem; 
            border-radius: 10px; 
            background-color: #f0f2f6;
            margin-bottom: 2rem;
        }
        .feature-box {
            padding: 1.5rem;
            border-radius: 8px;
            background-color: white;
            border: 1px solid #e0e0e0;
            margin-bottom: 1rem;
        }
        .success-box {
            padding: 1rem;
            border-radius: 8px;
            background-color: #d1fae5;
            border: 1px solid #34d399;
            margin-bottom: 1rem;
        }
        .warning-box {
            padding: 1rem;
            border-radius: 8px;
            background-color: #fff7ed;
            border: 1px solid #fb923c;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Main page header
st.markdown("""
    <div class="welcome-box">
        <h1>🎯 Debt Freedom Planner</h1>
        <h3>Your Smart Guide to Financial Freedom</h3>
        <p>Welcome to your personal debt management assistant! We use the powerful Avalanche method 
        to help you become debt-free faster while saving money on interest.</p>
    </div>
""", unsafe_allow_html=True)

# Authentication UI
if not st.session_state['logged_in']:
    st.markdown("""
        <div class="feature-box">
            <h3>🌟 Features</h3>
            <ul>
                <li>Create personalized debt repayment plans</li>
                <li>Track your progress and milestones</li>
                <li>Get smart recommendations for faster debt freedom</li>
                <li>Visualize your debt-free journey</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔑 Login", "✨ Create Account"])
    
    with auth_tab1:
        st.markdown("""
            <div style='padding: 1rem 0;'>
                <h3>Welcome Back! 👋</h3>
                <p>Log in to continue your journey to financial freedom.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            submit_login = st.form_submit_button("Login", use_container_width=True)
            
            if submit_login:
                if login_username in st.session_state['users']:
                    if st.session_state['users'][login_username] == hash_password(login_password):
                        st.session_state['logged_in'] = True
                        st.session_state['current_user'] = login_username
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Incorrect password!")
                else:
                    st.error("Username not found!")
    
    with auth_tab2:
        st.markdown("""
            <div style='padding: 1rem 0;'>
                <h3>Start Your Debt-Free Journey 🚀</h3>
                <p>Create an account to get personalized debt management plans and tracking.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("signup_form"):
            signup_username = st.text_input("Choose a Username", key="signup_username")
            signup_password = st.text_input("Create a Password", type="password", help="Choose a strong password to secure your account", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            submit_signup = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_signup:
                if not signup_username or not signup_password:
                    st.error("Please fill in all fields!")
                elif signup_password != signup_confirm:
                    st.error("Passwords don't match!")
                elif signup_username in st.session_state['users']:
                    st.error("Username already exists!")
                else:
                    st.session_state['users'][signup_username] = hash_password(signup_password)
                    if save_users():
                        st.success("Account created successfully! You can now login.")
                    else:
                        st.error("Failed to create account due to system error.")
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h4>Why Choose Our Debt Planner? 💡</h4>
            <p>Our app uses the Avalanche method, which has been proven to save you the most money in interest 
            while getting you debt-free as quickly as possible. We provide step-by-step guidance, progress tracking, 
            and smart recommendations tailored to your situation.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Show logout button if logged in
if st.session_state['logged_in']:
    st.sidebar.write(f"Welcome, {st.session_state.current_user}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

# Main navigation tabs

# Main navigation tabs
plan_setup, strategy, results = st.tabs(["📋 Plan Setup", "💡 Strategy", "📊 Results"])

# Strategy Tab
with strategy:
    st.markdown("""
        <div class="feature-box">
            <h2>💡 The Avalanche Method Explained</h2>
            <p>Understanding how the Avalanche method works will help you stay motivated and committed to your debt-free journey.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="success-box">
                <h3>✨ Benefits</h3>
                <ul>
                    <li>Pay less interest overall</li>
                    <li>Get out of debt faster</li>
                    <li>Mathematically optimal approach</li>
                    <li>Clear strategy to follow</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="warning-box">
                <h3>💪 Tips for Success</h3>
                <ul>
                    <li>Stay committed to the plan</li>
                    <li>Track your progress regularly</li>
                    <li>Celebrate small victories</li>
                    <li>Build an emergency fund</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### How It Works")
    st.markdown(lc_explain_strategy_avalanche())

# Plan Setup Tab
with plan_setup:
    st.markdown("""
        <div class="feature-box">
            <h2>🎯 Create Your Personalized Plan</h2>
            <p>Let's build a plan that fits your financial situation. We'll help you organize your debts 
            and create a realistic timeline for becoming debt-free.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="welcome-box">
            <h3>🧾 List Your Debts</h3>
            <p>Enter all your debts below. Include credit cards, personal loans, student loans, etc. 
            For best results, gather your latest statements before starting.</p>
        </div>
    """, unsafe_allow_html=True)
    
    count = st.number_input("How many debts do you have?", 
                           min_value=1, 
                           max_value=12, 
                           value=3, 
                           step=1,
                           help="Include all your debts that you want to pay off: credit cards, personal loans, etc.")
    
    hdr = st.columns([2,1,1,1])
    hdr[0].markdown("**Name**")
    hdr[1].markdown("**Balance ($)**")
    hdr[2].markdown("**Minimum ($/mo)**")
    hdr[3].markdown("**APR (%)**")
    
    debts: List[Debt] = []
    for i in range(int(count)):
        c0, c1, c2, c3 = st.columns([2,1,1,1])
        name = c0.text_input(f"name_{i}", value=f"Card {i+1}")
        bal  = c1.number_input(f"bal_{i}", min_value=0.0, step=10.0, value=1000.0, format="%0.2f")
        mmin = c2.number_input(f"min_{i}", min_value=0.0, step=5.0, value=35.0, format="%0.2f")
        apr  = c3.number_input(f"apr_{i}", min_value=0.0, step=0.5, value=20.0, format="%0.2f")
        debts.append(Debt(name=name, balance=bal, minimum=mmin, apr_percent=apr))

    st.markdown("## 💵 Budget & ⏱️ Target")
    b1, b2, b3, b4 = st.columns(4)
    net_income = b1.number_input("Net income ($/mo)", min_value=0.0, step=50.0, value=0.0, format="%0.2f")
    fixed_bills = b2.number_input("Fixed bills", min_value=0.0, step=25.0, value=0.0, format="%0.2f")
    essentials  = b3.number_input("Essential spend", min_value=0.0, step=25.0, value=0.0, format="%0.2f")
    buffer_amt  = b4.number_input("Safety buffer", min_value=0.0, step=25.0, value=200.0, format="%0.2f")

    mode = st.radio("I want to…", ["Finish in N months", "Finish by a date"], horizontal=True)
    if mode == "Finish in N months":
        target_months = int(st.number_input("Debt-free in (months)", 1, 120, 24, 1))
    else:
        by = st.date_input("Be debt-free by", value=date(date.today().year, min(12, date.today().month+6), 1))
        target_months = max(1, (by.year - date.today().year) * 12 + (by.month - date.today().month))

    if st.button("Build Plan", type="primary"):
        errs = validate_debts(debts)
        if errs:
            st.error("\n".join(errs))
        else:
            status = classify_status(net_income, fixed_bills, essentials, debts)
            safe_extra = safe_extra_from_budget(net_income, fixed_bills, essentials, buffer_amt, debts)
            req_extra  = required_extra_for_months(debts, target_months)
            gap        = max(0.0, req_extra - safe_extra)

            # For simulation display, use safe_extra (reality), not req_extra
            sim = run_simulation(debts, safe_extra, STRATEGY, [])

            ctx = {
                "status": status if status != "ok" else ("infeasible" if gap > 0 else "feasible"),
                "safe_extra": float(safe_extra),
                "required_extra": float(req_extra),
                "gap": float(gap),
                "target_months": int(target_months),
                "debts_summary": [{"name": d.name, "bal": d.balance, "min": d.minimum, "apr": d.apr_percent} for d in debts],
                "cash_summary": {"income": net_income, "fixed": fixed_bills, "essentials": essentials, "buffer": buffer_amt, "mins": sum_minimums(debts)},
            }
            st.session_state["plan_ctx"] = ctx
            st.session_state["sim"] = sim
            st.session_state["ui"]  = UserInput(debts=debts, strategy="avalanche", monthly_extra=safe_extra)

            # Build tasks via LangGraph → LLM
            g = build_graph()
            result = g.invoke(GraphState(context=ctx, tasks=[]))
            tasks = getattr(result, "tasks", [])
            st.session_state["tasks"] = tasks
            persist["tasks"] = [t.model_dump() for t in tasks]
            save_state(persist)
            st.success("Plan built.")

# Results Tab
with results:
    if "plan_ctx" not in st.session_state:
        st.markdown("""
            <div class="feature-box">
                <h2>📊 Your Journey to Financial Freedom</h2>
                <p>Once you've set up your plan, you'll see your personalized debt payoff timeline, 
                progress tracking, and smart recommendations here.</p>
                <br>
                <p>To get started:</p>
                <ol>
                    <li>Go to the "Setup Your Plan" tab</li>
                    <li>Enter your debts and budget information</li>
                    <li>Click "Build Plan" to see your personalized strategy</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)
    else:
        ctx = st.session_state["plan_ctx"]
        sim = st.session_state.get("sim")
        
        st.markdown("""
            <div class="feature-box">
                <h2>📊 Your Debt Freedom Plan</h2>
                <p>Here's your personalized plan based on your financial situation. We'll help you stay 
                on track and adjust as needed.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## 📌 Plan Feasibility")
        if ctx["status"] in {"zero_income", "infeasible"}:
            st.markdown("""
                <div class="warning-box">
                    <h3>⚠️ Adjustment Needed</h3>
                    <p>Your budget needs some adjustments to meet the target. See the guidance below 
                    for specific recommendations on how to make this work.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="success-box">
                    <h3>✅ Plan is Feasible</h3>
                    <p>Great news! Your budget aligns with your debt-free goals. Follow the plan 
                    consistently to achieve freedom from debt.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("### Recommendation")
        st.write(f"- **Required extra** for the target: **{dollars(ctx['required_extra'])}**/mo")
        st.write(f"- **Safe extra** from your budget: **{dollars(ctx['safe_extra'])}**/mo")
        if ctx["gap"] > 0:
            st.warning(f"You’re short by **{dollars(ctx['gap'])}**/mo. Adjust the date, trim expenses, or add income.")
        else:
            st.info("Your budget covers the target. Stay consistent.")

            st.markdown("### ⏳ Timeline")
            if sim:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Months to Freedom", sim.total_months)
                with col2:
                    st.metric("Total Interest", dollars(sim.total_interest))
                with col3:
                    st.metric("Debt-free Date", str(sim.debt_free_date(datetime.now().date())))
        
            if sim:
                st.markdown("### 📅 Detailed Payment Schedule")
                st.dataframe(sim.payoff_table(), use_container_width=True)

            st.markdown("---")
            st.markdown("### 🎯 Next Steps")
            st.markdown(lc_next_actions(ctx))

            st.markdown("### ✅ Action Items")
    if not st.session_state["tasks"]:
        st.info("No tasks yet. Click **Build Plan**.")
    else:
        for i, t in enumerate(st.session_state["tasks"]):
            c0, c1 = st.columns([0.08, 0.92])
            done = c0.checkbox("", value=t.done, key=f"task_{i}")
            t.done = bool(done)
            with c1.expander(f"{'✔️ ' if t.done else ''}{t.title}", expanded=False):
                st.write(t.description)
                if t.suggested_week:
                    st.caption(f"Suggested week: {t.suggested_week}")
        st.caption("Tasks are generated from your budget/target via LangGraph + OpenAI.")
