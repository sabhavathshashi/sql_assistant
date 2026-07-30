# 🤖 AI SQL Assistant for Databases

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Groq API](https://img.shields.io/badge/Groq-API-F55036.svg?style=flat)](https://console.groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, **AI-powered Natural Language to SQL (NL2SQL) Agent** that safely bridges the gap between non-technical stakeholders and complex relational databases. Powered by **Groq**, **FastAPI**, **SQLAlchemy**, and **SQLGlot**, the assistant dynamically inspects database schemas, translates plain English into dialect-accurate MySQL queries, enforces multi-layered read-only safety, and provides interactive execution through both a CLI and a REST API.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Security & Safety Framework](#security--safety-framework)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Environment Setup](#2-environment-setup)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Configure Credentials](#4-configure-credentials)
- [Usage](#usage)
  - [CLI](#option-a-command-line-interface-cli)
  - [REST API](#option-b-fastapi-rest-backend)
- [API Reference](#api-reference)
- [Example Session](#example-session)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Traditional data workflows often force non-technical team members — product managers, analysts, executives — to wait on engineering to write custom SQL for basic data retrieval. **SQL Assistant** removes this bottleneck by acting as a secure middleware agent that:

1. **Understands natural language** — interprets vague, multi-step, or business-oriented questions (e.g. *"What were our top 5 revenue products last month?"*).
2. **Ingests schema context safely** — inspects table structure, column types, and key constraints without exposing row-level data to the LLM.
3. **Enforces read-only safety** — validates every query's Abstract Syntax Tree (AST) to guarantee only `SELECT` / `WITH` statements are ever executed.
4. **Executes and explains** — runs the query inside a read-only transaction and returns structured data alongside a plain-English explanation.

---

## Key Features

- **Fast Groq integration** — uses the `groq` Python SDK with `llama-3.3-70b-versatile` by default for accurate, low-latency SQL generation.
- **Multi-layer read-only safety:**
  - **AST parsing (SQLGlot)** — rejects destructive statements (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`) at the syntax-tree level.
  - **Keyword filtering** — a secondary regex check blocks unauthorized SQL verbs.
  - **Database-level isolation** — every session runs under `SET TRANSACTION READ ONLY;`.
- **Dual runtime interfaces:**
  - **Interactive CLI** with pretty-printed tables (`tabulate`) and live connection health checks.
  - **FastAPI REST API** with fully async, OpenAPI-compliant endpoints and auto-generated Swagger docs.
- **Dynamic schema inspection** — automatic metadata extraction via SQLAlchemy inspectors keeps table/column mappings accurate as the schema evolves.
- **Plain-English explanations** — every generated query ships with a concise breakdown of its clauses (`JOIN`, `GROUP BY`, `HAVING`, window functions, etc.).

---

## System Architecture

```text
┌─────────────────────────┐
│   User Input / Prompt   │
└────────────┬─────────────┘
             │
             ▼
┌─────────────────────────┐      ┌───────────────────────────────┐
│  Schema Inspector        ├────► │ SQLAlchemy Inspector           │
│  (database.py)           │      │ Extracts tables & columns      │
└────────────┬─────────────┘      └───────────────────────────────┘
             │
             ▼
┌─────────────────────────┐      ┌───────────────────────────────┐
│  Groq LLM                ├────► │ Prompted with DB context       │
│  (agent.py)               │      │ Generates SQL + explanation    │
└────────────┬─────────────┘      └───────────────────────────────┘
             │
             ▼
┌─────────────────────────┐      ┌───────────────────────────────┐
│  SQL Safety Guard         ├────► │ SQLGlot AST parser              │
│  (agent.py)               │      │ Rejects DDL / DML mutations     │
└────────────┬─────────────┘      └───────────────────────────────┘
             │ (passes validation)
             ▼
┌─────────────────────────┐      ┌───────────────────────────────┐
│  MySQL Engine             ├────► │ READ ONLY session context       │
│  (database.py)            │      │ Executes the SELECT statement   │
└────────────┬─────────────┘      └───────────────────────────────┘
             │
             ▼
┌─────────────────────────┐
│  Output Data & Summary    │  (CLI table / REST JSON)
└─────────────────────────┘
```

---

## Security & Safety Framework

To prevent SQL injection, database mutation, and unauthorized administrative actions, SQL Assistant implements a strict three-tier protection stack:

| Layer | Mechanism | Protection Scope |
|---|---|---|
| **1. Prompt constraint** | System prompt rules | Instructs Groq to produce strictly standard ANSI/MySQL `SELECT` queries, with no comments or statement batching. |
| **2. AST parser** | SQLGlot parsing | Evaluates the full query tree — any non-`SELECT` node aborts execution before the database is ever contacted. |
| **3. Engine session** | Transaction locks | Issues `SET TRANSACTION READ ONLY;` per connection so MySQL itself rejects any modification attempt. |

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.10+ |
| API Framework | FastAPI, Uvicorn |
| LLM Engine | Groq Python SDK (`groq`), model `llama-3.3-70b-versatile` |
| Database Layer | SQLAlchemy (ORM/Core), PyMySQL driver |
| SQL Parsing & Validation | SQLGlot |
| Configuration | python-dotenv, Pydantic |
| CLI Utility | tabulate |

---

## Project Structure

```text
sql_assistant/
├── .env                  # Local environment configuration (secrets — not committed)
├── requirements.txt      # Python package dependencies
├── database.py           # Connection pooling and schema inspection logic
├── agent.py              # LLM prompt templates and AST safety engine
├── main.py                # FastAPI REST API endpoints and app lifecycle
├── cli.py                 # Interactive command-line runner
└── README.md              # Project documentation
```

---

## Getting Started

### Prerequisites

- **Python** 3.10 or higher
- **MySQL** 8.0+, running locally or on a remote host
- **Groq API key** from [GroqCloud](https://console.groq.com/keys)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/sql_assistant.git
cd sql_assistant
```

### 2. Environment Setup

Using a virtual environment is strongly recommended.

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Credentials

Create a `.env` file in the project root:

```env
# Groq API configuration
GROQ_API_KEY=your_actual_groq_api_key_here
# Optional: defaults to llama-3.3-70b-versatile
GROQ_MODEL=llama-3.3-70b-versatile

# MySQL connection parameters
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_database_name
```

> **Note:** Never commit `.env` to version control. Add it to `.gitignore`.

---

## Usage

### Option A: Command-Line Interface (CLI)

A lightweight terminal environment for ad-hoc querying.

```bash
python cli.py
```

**Workflow:**

1. The CLI inspects the database schema on startup.
2. Enter a natural language prompt when asked.
3. Review the generated SQL, explanation, and tabular results.
4. Type `q` or `exit` to close the session.

### Option B: FastAPI REST Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Once running:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## API Reference

### `POST /query`

Converts a natural language prompt into validated SQL, executes it, and returns structured results.

**Request**

```json
{
  "prompt": "Get the top 3 highest spending customers"
}
```

**Response — `200 OK`**

```json
{
  "sql": "SELECT customer_id, SUM(total_amount) AS total_spent FROM orders GROUP BY customer_id ORDER BY total_spent DESC LIMIT 3;",
  "explanation": "Aggregates total spend per customer from the orders table, orders results in descending order, and returns the top 3 records.",
  "data": [
    { "customer_id": 1042, "total_spent": 15230.50 },
    { "customer_id": 1089, "total_spent": 12400.00 },
    { "customer_id": 1012, "total_spent": 9850.75 }
  ]
}
```

**Error — `400 Bad Request`**

```json
{
  "detail": "SQL Execution Blocked: Forbidden keyword detected: DROP"
}
```

### `GET /schema`

Returns the cached database schema extracted by the dynamic inspector.

**Response — `200 OK`**

```json
{
  "schema": "Table 'customers': id (INTEGER), name (VARCHAR), email (VARCHAR)\nTable 'orders': id (INTEGER), customer_id (INTEGER), total_amount (DECIMAL)"
}
```

---

## Example Session

```text
==================================================
 🤖 AI SQL Assistant for MySQL (Read-Only Mode)
==================================================

[+] Inspecting database schema...
Table 'customers': customer_id (INTEGER), name (VARCHAR), created_at (DATETIME)
Table 'orders': order_id (INTEGER), customer_id (INTEGER), amount (DECIMAL), status (VARCHAR)

Ready! Ask any question about your database.

💬 Enter query: Which customers have spent more than 5000 in total?

⚙️ Generating SQL with Groq...

📝 Generated SQL:
   SELECT c.customer_id, c.name, SUM(o.amount) AS total_spent
   FROM customers c
   JOIN orders o ON c.customer_id = o.customer_id
   GROUP BY c.customer_id, c.name
   HAVING total_spent > 5000
   ORDER BY total_spent DESC;

💡 Explanation:
   Joins customers and orders, sums order amounts per customer, filters
   groups exceeding 5000 with HAVING, and orders by expenditure.

🚀 Executing query...

📊 Results (2 rows returned):

+---------------+---------------+---------------+
|  customer_id  |  name         |  total_spent  |
+---------------+---------------+---------------+
|  1042         |  Alice Smith  |  15230.50     |
|  1089         |  Bob Johnson  |  12400.00     |
+---------------+---------------+---------------+
```

---

## Roadmap

- [ ] **Multi-dialect support** — extend to PostgreSQL, SQLite, and Snowflake.
- [ ] **Chart & visualization generation** — render Chart.js / Matplotlib visuals alongside tabular responses.
- [ ] **Schema caching (Redis)** — reduce token overhead by caching schema state.
- [ ] **Streamlit / React dashboard** — a graphical web interface for non-technical users.

---

## Contributing

Contributions are welcome!

1. **Fork** the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. **Commit** your changes: `git commit -m 'Add new feature'`
4. **Push** the branch: `git push origin feature/your-feature-name`
5. Open a **Pull Request**.

---

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
