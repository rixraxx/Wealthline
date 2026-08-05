# Wealthline 📈

> **Personal Finance Intelligence Platform** — Upload bank statements, track budgets, and converse with an AI assistant grounded in your real financial data.

---

## 🚀 Overview

**Wealthline** is a full-stack personal finance application that pairs a robust financial management core with grounded AI capabilities. Instead of relying on manual tracking, Wealthline ingests financial documents, categorizes transactions automatically, and allows you to query your financial history in plain language.

### Key Capabilities
* 📄 **Document Processing:** Parse bank statements (PDF/OCR) into structured transactions via background queues.
* 🏷️ **Smart Categorization:** Automatic transaction tagging with confidence scores and manual override options.
* 📊 **Budgeting & Forecasting:** Account tracking, monthly budget enforcement, and trend-based spend projections.
* 💬 **"Ask Your Finances" AI:** Grounded RAG + tool-calling assistant that answers queries like *"How much did I spend on food in March vs April?"* or *"Am I on track to save ₹2L by December?"*

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend API** | FastAPI (Python 3.11+) |
| **Relational Database** | PostgreSQL + SQLAlchemy + Alembic |
| **Vector Database** | ChromaDB (Document retrieval & RAG) |
| **Background Processing** | Celery + Redis |
| **Frontend** | Flutter + Riverpod |
| **Infrastructure** | Docker Compose, S3-compatible Storage, GitHub Actions |

---

## 📂 Project Structure

```text
wealthline/
├── backend/              # FastAPI app, database models, background tasks & AI engines
├── frontend/             # Flutter application (Mobile / Web)
├── docs/                 # Architecture diagrams and specifications
├── docker-compose.yml    # Local infrastructure (Postgres, Redis)
└── README.md