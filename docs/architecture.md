\# Architecture



\## High-Level Flow



CSV → Azure Blob → Snowflake Stage → RAW → CURATED → Semantic View → Cortex Analyst → Streamlit



\## Components



\### Data Layer

\- Source data is loaded into Snowflake through RAW and CURATED layers.

\- The curated table standardizes product, chemical, category, and lifecycle date fields.



\### Semantic Layer

\- A semantic model is defined in `models/chemical\_products.yaml`.

\- The semantic view exposes business-friendly dimensions, time dimensions, metrics, and verified queries.



\### Analytics Layer

\- Cortex Analyst converts natural-language questions into answers and generated SQL.

\- The app displays both the answer and the SQL for transparency.



\### Application Layer

\- Streamlit provides the executive-style user interface.

\- Users can ask questions, review SQL, and inspect result tables.



\## Example User Flow



1\. User asks a question in plain English.

2\. Cortex Analyst interprets the request using the semantic view.

3\. Generated SQL is produced and executed.

4\. The app displays:

&#x20;  - answer

&#x20;  - SQL

&#x20;  - result table



\## Repo Artifacts



\- `streamlit\_app.py`

\- `models/chemical\_products.yaml`

\- `sql/create\_semantic\_view\_verify.sql`

\- `sql/create\_semantic\_view\_create.sql`

