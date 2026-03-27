# 💸 Debt Freedom Planner

An intelligent, task-driven financial planning application designed to help users become debt-free faster using structured workflows, dependency tracking, and guided financial decisions.

---

## 📌 Overview

The **Debt Freedom Planner** is a goal-oriented system that breaks down the journey to becoming debt-free into actionable, trackable tasks.

It leverages:

* Task dependency management
* Weekly planning guidance
* Financial prioritization strategies (like Avalanche method)

This project demonstrates backend logic design, data modeling, and integration with modern AI tooling.

---

## 🎯 Goal

> **"Become debt-free as soon as possible"**

The system generates and manages a structured plan based on:

* User experience level (Beginner)
* Availability (3 units/week)
* Monthly extra payment capacity ($200)
* Credit score (700)

---

## 🚀 Features

* ✅ Task-based debt payoff plan
* 🔗 Dependency-aware workflow (tasks unlock in order)
* 📅 Weekly execution roadmap
* 💰 Financial strategy guidance (APR prioritization)
* 📊 Structured JSON-driven planning engine
* 🔄 Progress tracking (`done` status)

---

## 🧠 Example Task Flow

```json id="7e2kq1"
{
  "title": "List debts & verify APRs",
  "depends_on": ["Enable autopay for minimums"],
  "suggested_week": 1
}
```

Tasks are:

* Sequentially structured
* Logically dependent
* Time-guided for realistic execution

---


## 🛠️ Tech Stack

**Frontend / UI:**

* Streamlit

**Backend / Logic:**

* Python
* Pydantic (data validation)

**Data Processing:**

* Pandas
* NumPy

**Environment Management:**

* python-dotenv

**AI Integration:**

* LangChain
* OpenAI

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```
git clone https://github.com/your-username/debt-freedom-planner.git
cd debt-freedom-planner
```

---

### 2. Create Virtual Environment

```
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3. Install Dependencies

```
pip install -r requirements.txt
```

---

### 4. Run the App
```
streamlit run app.py
```

---

## 📦 Dependencies

```txt id="y3l9vz"
streamlit>=1.36.0
pydantic>=2.7.0
pandas>=2.1.0
numpy>=1.26.0
python-dotenv>=1.0.1
langchain>=0.2.12
langchain-openai>=0.1.7
```

---

## 🧩 Data Model

The application uses a structured JSON schema:

* **goal_text** → User objective
* **availability** → Weekly effort capacity
* **experience** → Skill level
* **tasks** → Actionable steps with dependencies
* **monthly_extra** → Extra payment amount
* **credit_score** → Financial profile indicator

---

## 🔄 Example Workflow

1. Start with foundational financial safety (autopay)
2. Gather and verify all debt data
3. Calculate realistic extra payments
4. Optimize payoff strategy
5. Build financial buffer
6. Maintain weekly reviews

---

## 💡 Key Learnings

* Designing dependency-driven task systems
* Structuring financial workflows programmatically
* Using Pydantic for data validation
* Building interactive apps with Streamlit
* Integrating LLM-powered insights via LangChain

---

## 🔮 Future Improvements

* 📈 Debt payoff visualization dashboard
* 🔔 Smart reminders & notifications
* 🤖 AI-generated personalized strategies
* 🔐 User authentication & profiles
* ☁️ Cloud deployment (AWS / GCP)

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit a PR.

---

## 📧 Contact

For questions or collaboration, feel free to reach out.

---

⭐ If you found this project useful, consider giving it a star!
