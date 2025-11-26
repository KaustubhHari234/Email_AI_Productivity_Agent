# 📧 AI Email Productivity Agent

An intelligent, prompt-driven email management system powered by **Google Gemini**, **Pinecone**, and **MongoDB**.  
This agent automates email categorization, action-item extraction, semantic search, and professional reply drafting — all through a clean FastAPI backend and Streamlit UI.

---

## 🚀 Features

- **🧠 Prompt-Driven Intelligence**  
  Fully customizable “Prompt Brain” that controls how the AI categorizes emails, extracts tasks, and writes drafts.

- **📥 Smart Email Ingestion**  
  Load mock inbox data (or plug in real email sources) and automatically generate:  
  - Categories (Urgent, Action Required, Informational…)  
  - Priorities  
  - Extracted tasks & follow-ups  

- **🔍 RAG-Powered Search (Pinecone)**  
  Embed and store email content for semantic search:  
  _“Find emails related to customer issues”_  
  _“Show all urgent emails from last week”_

- **💬 Chat-Based Inbox Assistant**  
  Interact conversationally with your inbox:
  - Summaries  
  - Task extraction  
  - Email-level Q&A  
  - Inbox-wide reasoning  

- **✍️ Smart Draft Generation**  
  Auto-draft reply emails or new emails using your customized tone and full email context.

- **🎛️ Streamlit Frontend**  
  Simple, fast UI for browsing emails, chatting with the agent, and reviewing/editing drafts.

---

## 🏗️ Project Structure

```
email-productivity-agent/
├── backend/                 # FastAPI backend
│   ├── config/              # Configuration settings
│   ├── models/              # Pydantic models
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic (LLM, Vector, DB)
│   └── main.py              # Application entry point
├── data/                    # Data storage
│   └── mock_emails.json     # Sample data
├── frontend/                # Streamlit frontend
│   ├── components/          # UI components
│   ├── styles/              # CSS styles
│   └── app.py               # Frontend entry point
├── .env                     # Environment variables
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

---

## 🧰 Tech Stack

- 🐍 **Python 3.10+**
- ⚡ **FastAPI** — backend API services  
- 🧠 **Google Gemini** — LLM + embeddings  
- 🔎 **Pinecone Serverless** — vector search for RAG  
- 🐘 **MongoDB / Atlas** — storage for prompts, emails, drafts  
- 🖥️ **Streamlit** — frontend dashboard  
- 📦 **uv** — dependency & environment manager

---

## ⚙️ Prerequisites

You will need:

- Python ≥ 3.10  
- A running MongoDB instance (local or Atlas)  
- Pinecone API key + serverless index  
- Google Gemini API key  
- (Optional) Docker, if containerizing

---

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd email-productivity-agent
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add the following keys:

    ```env
    # Google Gemini
    GEMINI_API_KEY=your_gemini_api_key_here

    # Pinecone Vector DB
    PINECONE_API_KEY=your_pinecone_api_key_here
    PINECONE_ENVIRONMENT=us-east-1  # Or your specific region
    PINECONE_INDEX_NAME=email-agent

    # MongoDB
    MONGODB_URI=your_mongodb_connection_string
    MONGODB_DATABASE=email-agent
    ```

## Running the Application

The application consists of a FastAPI backend and a Streamlit frontend. You need to run both terminals.

### 1. Start the Backend
Open a terminal and run:
```bash
uvicorn backend.main:app --reload
```
The backend will start at `http://localhost:8000`.

### 2. Start the Frontend
Open a second terminal and run:
```bash
streamlit run frontend/app.py
```
The UI will open in your browser at `http://localhost:8501`.


## ☁️ Deployment on Streamlit Cloud

1.  **Push your code to GitHub.**
2.  **Log in to [Streamlit Cloud](https://streamlit.io/cloud).**
3.  **Create a new app** and select your repository.
4.  **Configure Secrets:**
    - Before deploying (or in the app settings after deployment), go to **"Advanced Settings"** -> **"Secrets"**.
    - Add the contents of your `.env` file here in TOML format:
    ```toml
    GEMINI_API_KEY = "your_gemini_api_key_here"
    PINECONE_API_KEY = "your_pinecone_api_key_here"
    PINECONE_ENVIRONMENT = "us-east-1"
    PINECONE_INDEX_NAME = "email-agent"
    MONGODB_URI = "your_mongodb_connection_string"
    MONGODB_DATABASE = "email-agent"
    ```
5.  **Deploy!**



## 📥 How to Use

### 1. Load Emails (Phase 1)
- Go to “Email Ingestion & Prompt Brain” section.
- Click **Load & Process Mock Emails**.
- Emails will be:
    - Categorized
    - Embedded using Gemini
    - Stored in Pinecone & MongoDB

### 2. Configure the Prompt Brain
- You can edit three core prompts:
    - Categorization
    - Action Item Extraction
    - Auto-Reply Drafting
- Changes apply instantly across the system.

### 3. Chat With the Email Agent (Phase 2)
- Example queries:
    - “Summarize this email.”
    - “What tasks do I need to do?”
    - “Show me all urgent emails.”
    - “Find emails about project roadmap.”
- The agent uses:
    - Email text
    - Your Prompt Brain rules
    - Pinecone RAG context
    - Gemini reasoning

### 4. Generate Draft Replies (Phase 3)
- Select an email → add instructions → **Generate Draft**
- OR create a new email from scratch
- Edit subject/body in the UI
- Drafts are stored safely — never sent automatically

## 🧭 Roadmap / Future Enhancements

- 📬 Gmail / Outlook real inbox integration
- 🧠 Domain-specific prompt templates (sales, HR, dev, marketing)
- 🗃️ Multi-user accounts + authentication
- 📊 Analytics dashboard
- 📝 Improved drafting UI (tone presets, markdown editor)

## 🛡️ Security Notes

- Do NOT commit `.env` or API keys.
- Rotate keys if leaked.
- Use secret managers in production.
- Apply usage limits for Gemini & Pinecone.

## 📄 License

Distributed under the MIT License.
Feel free to use, modify, and distribute with attribution.
