from datetime import timedelta

import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Chemical Products Analyst",
    page_icon=":material/science:",
    layout="wide",
)

SEMANTIC_VIEW = "CHEM_DB.CURATED.CHEMICAL_PRODUCTS_SEMANTIC"

SUGGESTIONS = [
    "Which companies have the most chemical products?",
    "What are the top primary categories by number of products?",
    "How many products were discontinued each year?",
    "Which products contain a specific chemical?",
]


# ---------------------------------------------------------------------------
# Cortex Analyst helpers (unchanged)
# ---------------------------------------------------------------------------
def get_cortex_analyst_response(conn, question: str, chat_history: list[dict]) -> dict:
    """Send a question to Cortex Analyst via the REST API."""
    raw = conn.raw_connection
    token = raw._rest._token
    account_url = raw._rest._host

    url = f"https://{account_url}/api/v2/cortex/analyst/message"
    headers = {
        "Authorization": f'Snowflake Token="{token}"',
        "Content-Type": "application/json",
    }

    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append({"role": "user", "content": [{"type": "text", "text": msg["content"]}]})
        elif msg["role"] == "analyst":
            messages.append({"role": "analyst", "content": msg["raw_content"]})

    messages.append({"role": "user", "content": [{"type": "text", "text": question}]})

    payload = {
        "messages": messages,
        "semantic_view": SEMANTIC_VIEW,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def parse_analyst_response(response: dict) -> dict:
    """Extract text, SQL, and result data from the Cortex Analyst response."""
    message = response.get("message", {})
    content_items = message.get("content", [])

    text_parts = []
    sql = None

    for item in content_items:
        if item.get("type") == "text":
            text_parts.append(item["text"])
        elif item.get("type") == "sql":
            sql = item["statement"]

    return {
        "text": "\n\n".join(text_parts) if text_parts else "",
        "sql": sql,
        "raw_content": content_items,
    }


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
conn = st.connection("snowflake")


# ---------------------------------------------------------------------------
# KPI loader (cached)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=timedelta(minutes=10), show_spinner=False)
def load_kpis():
    row = conn.query("""
        SELECT
            COUNT(*)                        AS total_products,
            COUNT(DISTINCT CHEMICALNAME)    AS distinct_chemicals,
            COUNT(DISTINCT COMPANYNAME)     AS distinct_companies,
            COUNT(DISTINCT PRIMARYCATEGORY) AS distinct_categories
        FROM CHEM_DB.CURATED.CHEMICAL_PRODUCTS
    """).iloc[0]
    return row


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header(":material/science: Chemical Products Analyst")
    st.caption("Powered by Snowflake Cortex Analyst")

    st.subheader("Suggested questions", divider=True)
    for i, q in enumerate(SUGGESTIONS):
        if st.button(q, key=f"suggestion_{i}", icon=":material/chat:"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()

    st.subheader("About", divider=True)
    st.caption(
        "This app uses **Cortex Analyst** to translate natural-language "
        "questions into SQL against the `CHEMICAL_PRODUCTS` semantic view, "
        "then executes the query and returns results."
    )
    with st.container(border=True):
        st.markdown(":material/database: **Semantic view**")
        st.code(SEMANTIC_VIEW, language=None)

    if st.button("Clear conversation", icon=":material/delete:"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
header_left, header_right = st.columns([3, 1], vertical_alignment="bottom")
with header_left:
    st.title("Chemical products intelligence")
    st.caption("Ask questions in plain English — get executive-ready answers backed by live data")
with header_right:
    st.badge("Connected to Snowflake Cortex Analyst", icon=":material/check_circle:", color="green")

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
try:
    kpis = load_kpis()
    with st.container(horizontal=True):
        st.metric("Total products", f"{kpis['TOTAL_PRODUCTS']:,}", border=True)
        st.metric("Distinct chemicals", f"{kpis['DISTINCT_CHEMICALS']:,}", border=True)
        st.metric("Companies", f"{kpis['DISTINCT_COMPANIES']:,}", border=True)
        st.metric("Categories", f"{kpis['DISTINCT_CATEGORIES']:,}", border=True)
except Exception:
    st.caption(":material/info: KPI summary unavailable — ask a question below to get started.")

# ---------------------------------------------------------------------------
# Render helper for analyst messages
# ---------------------------------------------------------------------------
def render_analyst_message(msg, *, expanded_sql: bool = False):
    """Render an analyst response with insight card, SQL expander, and data table."""
    if msg.get("text"):
        st.markdown(msg["text"])
    if msg.get("sql"):
        with st.expander(":material/code: Generated SQL", expanded=expanded_sql, icon=":material/database:"):
            st.code(msg["sql"], language="sql")
    if msg.get("df") is not None and not msg["df"].empty:
        with st.container(border=True):
            st.markdown(f":material/table_chart: **Query results** — {len(msg['df']):,} rows")
            st.dataframe(msg["df"], hide_index=True)


# ---------------------------------------------------------------------------
# Conversation area
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    with st.container(border=True):
        st.markdown(
            ":material/lightbulb: **Get started** — type a question below or pick one "
            "from the sidebar to explore chemical product data."
        )
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"] if msg["role"] != "analyst" else "assistant"):
            if msg["role"] == "analyst":
                render_analyst_message(msg)
            else:
                st.write(msg["content"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if prompt := st.chat_input("Ask a question about chemical products..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# ---------------------------------------------------------------------------
# Process last user message if unanswered
# ---------------------------------------------------------------------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    question = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                history = st.session_state.messages[:-1]
                response = get_cortex_analyst_response(conn, question, history)
                parsed = parse_analyst_response(response)

                text = parsed["text"]
                sql = parsed["sql"]
                raw_content = parsed["raw_content"]
                df = pd.DataFrame()

                if text:
                    st.markdown(text)

                if sql:
                    with st.expander(":material/code: Generated SQL", expanded=True, icon=":material/database:"):
                        st.code(sql, language="sql")
                    df = conn.query(sql)
                    if not df.empty:
                        with st.container(border=True):
                            st.markdown(f":material/table_chart: **Query results** — {len(df):,} rows")
                            st.dataframe(df, hide_index=True)
                    else:
                        st.info("Query returned no results.", icon=":material/info:")

                st.session_state.messages.append({
                    "role": "analyst",
                    "content": text,
                    "text": text,
                    "sql": sql,
                    "df": df,
                    "raw_content": raw_content,
                })

            except requests.exceptions.HTTPError as e:
                error_detail = e.response.text if e.response is not None else str(e)
                st.error(f"Cortex Analyst error: {error_detail}", icon=":material/error:")
            except Exception as e:
                st.error(f"Error: {e}", icon=":material/error:")
