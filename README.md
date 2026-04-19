\# Chemical Products Intelligence



Executive-style Streamlit dashboard powered by Snowflake Cortex Analyst, Semantic Views, and Cortex Code CLI for natural-language analytics over structured chemical product data.



\## Overview



This project demonstrates a Snowflake-native analytics application that lets users ask business questions in plain English and receive:



\- executive-style natural language answers

\- generated SQL

\- live tabular results



\## Architecture



CSV → Azure Blob → Snowflake Stage → RAW → CURATED → Semantic View → Cortex Analyst → Streamlit



\## Tech Stack



\- Snowflake

\- Snowflake Cortex Analyst

\- Semantic Views

\- Cortex Code CLI

\- Streamlit

\- Python



\## Key Features



\- Natural language to SQL

\- Semantic layer for governed analytics

\- Executive-style dashboard

\- Suggested business questions

\- Multi-turn chat experience

\- Generated SQL visibility

\- Live result tables



\## Project Structure



\- `streamlit\_app.py` — main Streamlit application

\- `models/chemical\_products.yaml` — semantic model YAML

\- `sql/create\_semantic\_view\_verify.sql` — semantic view validation SQL

\- `sql/create\_semantic\_view\_create.sql` — semantic view creation SQL

\- `.streamlit/config.toml` — Streamlit theme configuration



\## How to Run Locally



1\. Configure your Snowflake connection locally.

2\. Start the app:



```bash

streamlit run streamlit\_app.py

