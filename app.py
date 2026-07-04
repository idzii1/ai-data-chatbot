import re
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="AI Data Analyst Platform",
    page_icon="📊",
    layout="wide"
)

# =====================
# DATABASE
# =====================
# If you want persistence between reruns/restarts, replace ':memory:' with 'app.db'
conn = sqlite3.connect(":memory:", check_same_thread=False)

# =====================
# TITLE
# =====================
st.title("🤖 AI Data Analyst Platform")
st.caption("Python + SQL + Streamlit")

# =====================
# FILE UPLOAD
# =====================
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Validation
        required_cols = {"Sales", "Category"}
        missing = required_cols - set(df.columns)
        if missing:
            st.error(f"Missing required columns: {', '.join(sorted(missing))}")
            st.stop()

        # Cleaning
        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
        df = df.dropna(subset=["Sales"]).copy()
        df["Category"] = df["Category"].astype(str).str.strip()

        if "Month" in df.columns:
            df["Month"] = df["Month"].astype(str).str.strip().str.title()

        df.to_sql("sales", conn, index=False, if_exists="replace")
        st.success("Dataset loaded successfully ✅")

    except Exception as e:
        st.error(f"Upload/parse error: {e}")
        st.stop()
else:
    st.info("Upload ecommerce.csv to continue")
    st.stop()

# =====================
# KPI
# =====================
try:
    revenue = pd.read_sql_query(
        """
        SELECT ROUND(SUM(Sales), 2) AS Revenue
        FROM sales
        """,
        conn
    )

    orders = pd.read_sql_query(
        """
        SELECT COUNT(*) AS Orders
        FROM sales
        """,
        conn
    )
except Exception as e:
    st.error(f"KPI query error: {e}")
    st.stop()

col1, col2 = st.columns(2)

col1.metric("💰 Revenue", f"${float(revenue.iloc[0, 0]):,.2f}")
col2.metric("📦 Orders", int(orders.iloc[0, 0]))

# =====================
# DASHBOARD
# =====================
st.subheader("📊 Revenue by Category")

try:
    category_df = pd.read_sql_query(
        """
        SELECT
            Category,
            ROUND(SUM(Sales), 2) AS Total_Sales
        FROM sales
        GROUP BY Category
        ORDER BY Total_Sales DESC
        """,
        conn
    )

    fig = px.bar(
        category_df,
        x="Category",
        y="Total_Sales",
        color="Category",
        title="Revenue by Category"
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Dashboard query error: {e}")

# =====================
# CHAT MEMORY
# =====================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            st.code(msg["sql"], language="sql")
        if "df" in msg:
            st.dataframe(msg["df"], use_container_width=True)
        if "fig" in msg:
            st.plotly_chart(msg["fig"], use_container_width=True)

# =====================
# NLP + SQL
# =====================
MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def extract_top_n(question: str, default_n: int = 1) -> int:
    m = re.search(r"\btop\s+(\d+)\b", question.lower())
    if m:
        return max(1, min(int(m.group(1)), 20))
    return default_n

def answer_question(question: str):
    q = question.lower().strip()

    # revenue
    if "revenue" in q and "category" not in q:
        sql = """
        SELECT ROUND(SUM(Sales), 2) AS Revenue
        FROM sales
        """
        result = pd.read_sql_query(sql, conn)
        text = f"Total revenue = **${float(result.iloc[0, 0]):,.2f}**"
        return {"text": text, "sql": sql, "df": result}

    # top n categories (e.g., "top 3 categories")
    if "top" in q and "categor" in q:
        n = extract_top_n(q, default_n=1)
        sql = f"""
        SELECT
            Category,
            ROUND(SUM(Sales), 2) AS Revenue
        FROM sales
        GROUP BY Category
        ORDER BY Revenue DESC
        LIMIT {n}
        """
        result = pd.read_sql_query(sql, conn)
        fig = px.bar(result, x="Category", y="Revenue", color="Category", title=f"Top {n} Categories")
        text = f"Top **{len(result)}** categories:"
        return {"text": text, "sql": sql, "df": result, "fig": fig}

    # top category
    if "top category" in q:
        sql = """
        SELECT
            Category,
            ROUND(SUM(Sales), 2) AS Revenue
        FROM sales
        GROUP BY Category
        ORDER BY Revenue DESC
        LIMIT 1
        """
        result = pd.read_sql_query(sql, conn)
        text = f"Top category: **{result.iloc[0]['Category']}**"
        return {"text": text, "sql": sql, "df": result}

    # category table/chart
    if "category" in q:
        sql = """
        SELECT
            Category,
            ROUND(SUM(Sales), 2) AS Revenue
        FROM sales
        GROUP BY Category
        ORDER BY Revenue DESC
        """
        result = pd.read_sql_query(sql, conn)
        fig = px.pie(result, values="Revenue", names="Category", title="Sales by Category")
        return {"text": "Revenue by category:", "sql": sql, "df": result, "fig": fig}

    # trend
    if "trend" in q or "over time" in q or "month" in q:
        # requires Month column
        cols = pd.read_sql_query("PRAGMA table_info(sales)", conn)["name"].tolist()
        if "Month" not in cols:
            return {"text": "This dataset has no `Month` column, so trend cannot be computed."}

        sql = """
        SELECT
            Month,
            ROUND(SUM(Sales), 2) AS Revenue,
            CASE Month
                WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
                WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
                ELSE 99
            END AS Month_Order
        FROM sales
        GROUP BY Month
        ORDER BY Month_Order
        """
        result = pd.read_sql_query(sql, conn)
        fig = px.line(result, x="Month", y="Revenue", markers=True, title="Monthly Revenue Trend")
        return {"text": "Sales trend over time:", "sql": sql, "df": result[["Month", "Revenue"]], "fig": fig}

    return {
        "text": (
            "Try:\n"
            "- revenue\n"
            "- top category\n"
            "- top 3 categories\n"
            "- category\n"
            "- trend"
        )
    }

# =====================
# QUICK ACTIONS
# =====================
st.markdown("**Quick Actions:**")
suggestions = ["Revenue", "Top category", "Top 3 categories", "Category", "Trend"]
cols = st.columns(len(suggestions))

for i, s in enumerate(suggestions):
    if cols[i].button(s):
        st.session_state["pending_query"] = s

# =====================
# CHAT
# =====================
question = st.chat_input("Ask about your data...")

if "pending_query" in st.session_state:
    question = st.session_state.pop("pending_query")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    try:
        result = answer_question(question)
    except Exception as e:
        result = {"text": f"Query error: {e}"}

    assistant_msg = {"role": "assistant", "content": result["text"]}
    if "sql" in result:
        assistant_msg["sql"] = result["sql"]
    if "df" in result:
        assistant_msg["df"] = result["df"]
    if "fig" in result:
        assistant_msg["fig"] = result["fig"]

    st.session_state.messages.append(assistant_msg)

    with st.chat_message("assistant"):
        st.markdown(result["text"])
        if "sql" in result:
            st.code(result["sql"], language="sql")
        if "df" in result:
            st.dataframe(result["df"], use_container_width=True)
        if "fig" in result:
            st.plotly_chart(result["fig"], use_container_width=True)
 
