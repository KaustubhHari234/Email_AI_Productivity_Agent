<div align="center">

# Email AI Productivity Agent

### A Multi-Agent, Prompt-Driven Inbox Assistant

*Categorize emails, extract action items, search semantically, and draft replies — all through a fully customizable Prompt Brain powered by Google Gemini, Pinecone, and MongoDB.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Gemini%202.0%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-blueviolet)](https://www.pinecone.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## Overview

**Email AI Productivity Agent** is an end-to-end inbox copilot that turns a chaotic mailbox into a structured, queryable knowledge base. Four specialized agents collaborate behind a single FastAPI orchestrator and a tab-based Streamlit UI to help you triage, search, and respond to email at the speed of thought.

The entire system is steered by a **Prompt Brain** — a small set of editable prompts persisted in MongoDB. Tweak the prompts, and the agents' behavior changes instantly across categorization, action-item extraction, and reply drafting.

---

## Highlights

- **Four collaborating agents** — categorization, action-item extraction, RAG Q&A, and draft generation
- **Prompt Brain** — versioned, hot-swappable prompts stored in MongoDB control every agent's behavior
- **Hybrid storage** — Pinecone for semantic recall, MongoDB for structured records (emails, prompts, drafts)
- **Domain-quality embeddings** — Google `text-embedding-004` via LangChain wrapper
- **Resilient LLM calls** — Tenacity-backed retry with exponential backoff on Gemini failures
- **Strict JSON contracts** — categorization & action-item agents return parseable JSON the orchestrator can trust
- **Tabbed Streamlit UI** — Inbox, Prompt Brain, Agent Chat, and Drafts in one cohesive workspace
- **Zero send-by-default safety** — drafts are always saved, never auto-sent

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Streamlit Frontend                       │
│   Inbox  │  Prompt Brain  │  Agent Chat  │  Drafts               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                   ┌─────────▼──────────┐
                   │   FastAPI Backend  │
                   │ EmailProductivity- │
                   │      Backend       │
                   └─────────┬──────────┘
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌─────────▼────────┐   ┌──────▼──────┐
│ Categoriz-   │   │  Action Item     │   │  RAG Agent  │
│ ation Agent  │   │     Agent        │   │             │
└──────────────┘   └──────────────────┘   └─────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌─────────▼────────┐   ┌──────▼──────┐
│ LLMService   │   │ VectorService    │   │ DatabaseSvc │
│ (Gemini)     │   │  (Pinecone)      │   │  (MongoDB)  │
└──────────────┘   └──────────────────┘   └─────────────┘
                             │
                   ┌─────────▼──────────┐
                   │    Draft Agent     │
                   └────────────────────┘
```

### Three-phase processing pipeline

| Phase | Stage | What happens |
|-------|-------|--------------|
| **1** | Ingestion & Knowledge Base | Emails → categorized → action items extracted → embedded → upserted into Pinecone & MongoDB |
| **2** | Email Processing (RAG) | Free-form questions → top-k vector retrieval → Gemini answers with sources & confidence |
| **3** | Draft Generation | Reply / new email / refine workflows → drafts saved to MongoDB (never auto-sent) |

---

## The Four Agents

| Agent | Responsibility | Output Contract |
|-------|----------------|-----------------|
| **CategorizationAgent** | Classify each email | `URGENT`, `ACTION_REQUIRED`, `INFORMATIONAL`, `SPAM`, `UNCATEGORIZED` + reason |
| **ActionItemAgent** | Extract follow-ups | List of `{description, priority, deadline, completed}` |
| **RAGAgent** | Answer inbox questions | `{answer, sources, confidence}` from top-k Pinecone matches |
| **DraftAgent** | Compose replies & new emails | `EmailDraft` with subject, body, suggested follow-ups |

Each agent reads its **active prompt** from MongoDB at runtime — no redeploy needed when you edit a prompt in the Prompt Brain UI.

---

## Project Structure

```
Email_AI_Productivity_Agent/
│
├── backend/                         FastAPI orchestrator
│   ├── main.py                      EmailProductivityBackend + REST endpoints
│   ├── agents/
│   │   ├── categorization_agent.py  Category + reason
│   │   ├── action_item_agent.py     Task extraction
│   │   ├── rag_agent.py             Pinecone-backed Q&A
│   │   └── draft_agent.py           Reply / new / refine drafts
│   ├── services/
│   │   ├── llm_service.py           Gemini wrapper (with Tenacity retries)
│   │   ├── vector_service.py        Pinecone Serverless + Google embeddings
│   │   ├── database_service.py      MongoDB collections & indexes
│   │   └── email_service.py         Load mock emails + full pipeline
│   ├── models/
│   │   ├── email.py                 Email, ActionItem, EmailCategory enum
│   │   ├── prompt.py                PromptConfig, PromptLibrary
│   │   └── draft.py                 EmailDraft
│   ├── config/
│   │   └── settings.py              Pydantic-settings (env-driven)
│   └── utils/
│       └── helpers.py
│
├── frontend/                        Streamlit UI
│   ├── app.py                       4-tab dashboard
│   ├── components/
│   │   ├── email_list.py            Inbox list & details
│   │   ├── prompt_editor.py         Prompt Brain editor
│   │   ├── agent_chat.py            RAG conversation panel
│   │   └── draft_editor.py          Draft authoring & refinement
│   └── styles/custom.css
│
├── data/
│   ├── mock_emails.json             Seed inbox for demos
│   └── knowledge_base/              Future: real-source connectors
│
├── tests/
│   ├── test_agents.py
│   └── test_services.py
│
├── main.py                          Hello-world entrypoint
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend API** | FastAPI 0.115, Uvicorn |
| **Frontend** | Streamlit 1.40 |
| **LLM** | Google Gemini 2.0 Flash (`google-generativeai` 0.8.3) |
| **Embeddings** | Google `text-embedding-004` via `langchain-google-genai` |
| **Vector Store** | Pinecone (Serverless, AWS, cosine, dim=768) |
| **Database** | MongoDB (`pymongo` 4.9 sync, `motor` 3.6 async) |
| **Orchestration** | LangChain Core / Community 0.3.7 |
| **Validation** | Pydantic 2 + `pydantic-settings` |
| **Resilience** | Tenacity (exponential backoff, 3 attempts) |
| **Testing** | Pytest + pytest-asyncio |

---

## Getting Started

### 1. Prerequisites

- Python **3.10+**
- A **MongoDB** connection (local or Atlas)
- A **Pinecone** Serverless account + API key
- A **Google AI Studio** API key for Gemini

### 2. Install

```bash
git clone https://github.com/<your-username>/Email_AI_Productivity_Agent.git
cd Email_AI_Productivity_Agent

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file at the project root:

```env
# Google Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048
EMBEDDING_MODEL=models/text-embedding-004

# Pinecone Serverless
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=email-agent
PINECONE_DIMENSION=768
PINECONE_METRIC=cosine

# MongoDB
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net
MONGODB_DATABASE=email-agent

# Application
LOG_LEVEL=INFO
MAX_EMAILS_DISPLAY=50
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 4. Run the backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

OpenAPI docs: **http://localhost:8000/docs**

### 5. Run the Streamlit UI

```bash
streamlit run frontend/app.py
```

Open **http://localhost:8501** and click **Load Emails** in the sidebar to seed the system from `data/mock_emails.json`.

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Health check |
| `POST` | `/emails/process?source=mock` | Run the full ingestion pipeline |
| `GET`  | `/emails` | List emails (filter by category, paginate) |
| `GET`  | `/emails/{email_id}` | Fetch a single email |
| `GET`  | `/inbox/summary` | LLM-generated inbox summary |
| `GET`  | `/inbox/query?q=...` | RAG-powered semantic Q&A |
| `GET`  | `/action-items` | Aggregated action items, priority-sorted |
| `GET`  | `/drafts` | List saved drafts |

### Sample RAG response

```json
{
  "answer": "Three urgent emails reference the Q2 roadmap deadline...",
  "sources": [
    { "id": "e_142", "score": 0.91, "metadata": { "subject": "Q2 Roadmap", "sender": "alice@acme.com" } }
  ],
  "confidence": "high"
}
```

---

## How the Prompt Brain Works

Three prompts steer the system. Each one is stored as a versioned `PromptConfig` in MongoDB:

| Prompt Type | Used By | Default Behavior |
|-------------|---------|------------------|
| `categorization` | CategorizationAgent | Bucket emails into 4 categories with a reason |
| `action_item` | ActionItemAgent | Extract tasks with priority and deadline |
| `reply_draft` | DraftAgent | Generate professional, concise replies |

Edit any prompt in the **Prompt Brain** tab, hit save, and the next agent invocation reads the new prompt from MongoDB — no restart, no redeploy.

---

## Streamlit Workflow

1. **Load Emails** — pull mock inbox, run categorization + action extraction + Pinecone upsert
2. **Inbox tab** — browse, filter, view details, get one-click summaries
3. **Prompt Brain tab** — edit categorization, action-item, and reply prompts
4. **Agent Chat tab** — ask anything: *"What did Sarah send last week?"*, *"Show me urgent items"*, *"Summarize the budget thread"*
5. **Drafts tab** — generate replies from any email, draft new emails from instructions, refine iteratively

---

## Deployment — Streamlit Cloud

1. Push this repo to GitHub.
2. Create a new app at **[streamlit.io/cloud](https://streamlit.io/cloud)** pointing to `frontend/app.py`.
3. Under **Advanced Settings → Secrets**, paste:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
PINECONE_API_KEY = "your_pinecone_api_key"
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = "email-agent"
MONGODB_URI = "your_mongodb_connection_string"
MONGODB_DATABASE = "email-agent"
```

4. Deploy.

---

## Testing

```bash
pytest tests/ -v
```

Tests cover both agent orchestration (`test_agents.py`) and the underlying services (`test_services.py`).

---

## Roadmap

- [ ] Real Gmail / Outlook OAuth ingestion
- [ ] Multi-user accounts with row-level access control
- [ ] Streaming token responses in the chat panel
- [ ] Tone presets (formal / friendly / terse) for drafts
- [ ] Analytics dashboard: response-time, action-item burn-down, sender heatmap
- [ ] Domain-specific prompt packs (sales, HR, engineering, support)
- [ ] Dockerfile + docker-compose for one-command deployment

---

## Security Notes

- Never commit `.env` files or API keys; rotate any key that leaks
- Use a secrets manager (AWS Secrets Manager, GCP Secret Manager, or Streamlit Secrets) in production
- Tighten CORS and add an auth layer (OAuth2 / JWT) before exposing the API publicly
- Drafts are **never** auto-sent — every send must be a deliberate user action

---

## License

Distributed under the **MIT License**. See `LICENSE` for the full text.

---

<div align="center">

**Built with FastAPI, Streamlit, LangChain, Pinecone, and Gemini.**

*If this project helped you, consider leaving a star.*

</div>
