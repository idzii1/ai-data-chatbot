# 🤖 AI Data Analyst Platform

Simple interactive analytics app built with **Python + SQL + Streamlit**.

The app allows you to:

- upload a CSV dataset,
- run SQL-based analysis,
- view KPIs and charts,
- ask questions in a chat interface (rule-based NLP).

---

## 🚀 Features

- **CSV upload** (`.csv`)
- Data stored in SQLite table: `sales`
- **KPI cards**:
  - Total Revenue
  - Total Orders
- **Dashboard chart**:
  - Revenue by Category (bar chart)
- **Chat assistant** with SQL-backed responses:
  - `revenue`
  - `top category`
  - `top 3 categories`
  - `category`
  - `trend` (if `Month` column exists)
- Chat memory in `st.session_state`
- Quick action buttons for common questions

---

## 🧱 Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- SQLite (`sqlite3`)
- Plotly Express

---

## 📂 Project Structure

```text
.
├── app.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

1. Clone or download the project.
2. (Optional) Create virtual environment.
3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## ▶️ Run the app

```bash
python -m streamlit run app.py
```

Then open the local Streamlit URL shown in terminal (usually `http://localhost:8501`).

---

## 📄 CSV Requirements

Minimum required columns:

- `Sales`
- `Category`

Optional (needed for trend analysis):

- `Month` (recommended format: `Jan`, `Feb`, ..., `Dec`)

Example header:

```csv
Order_ID,Customer_ID,Category,Sales,Month
```

---

## 💬 Supported Chat Queries

Examples:

- `revenue`
- `top category`
- `top 3 categories`
- `category`
- `trend`
- `show trend over time`
- `revenue by category`

---

## 🧠 How chat logic works

The assistant uses simple rule-based intent detection in Python:

- detects keywords in the user question,
- builds SQL query,
- runs query on SQLite table `sales`,
- returns text + optional dataframe + optional chart.

---

## ⚠️ Notes

- Current database connection uses `:memory:` (in-memory SQLite), so data is reset when app restarts.
- To persist data, change:

```python
sqlite3.connect(":memory:", check_same_thread=False)
```

to:

```python
sqlite3.connect("app.db", check_same_thread=False)
```

---

## 🔮 Possible Improvements

- Sidebar filters (Category/Month) connected with chat
- Better NLP (more intents and synonyms)
- User authentication
- Download query results as CSV
- LLM-based text-to-SQL (optional, paid API)

---

## Screenshots

### Dashboard

screenshots/dashboard.png

### AI SQL Chat

screenshots/chatbot.png

### Sales Trend Analysis

screenshots/trend.png


## 👨‍💻 Author

Igor Michalak
AI Data Analyst Platform project
