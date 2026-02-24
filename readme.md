# 🧘 Personal AI Companion

A supportive, insightful, and proactive personal AI companion designed to help you navigate your daily life. Built with Python, Streamlit, and the latest LangChain Agents, this companion remembers your goals, preferences, and challenges to provide personalized coaching and support.

## 🚀 Features

- **Personalized Onboarding**: The agent gets to know you through a series of thoughtful questions.
- **Persistent Personal Memory**: Remembers your goals, stressors, and preferences using dedicated memory tools.
- **Conversational Awareness**: Maintains state across messages using `InMemorySaver`.
- **Modern AI Infrastructure**: Powered by Groq (Llama 3.1) and managed with **uv**.
- **GitOps Ready**: Fully automated CI/CD pipeline for Kubernetes deployment.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Agent Framework**: [LangChain](https://www.langchain.com/) (latest `create_agent` patterns)
- **Memory Management**: LangGraph `InMemorySaver` + Custom JSON-based profile storage
- **Engine**: [Groq](https://groq.com/) (Llama 3.1 8B)
- **Orchestration**: Kubernetes
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)

## 📂 Project Structure

```text
personal-study-ai-agent/
│
├── application.py          # Main Chat UI
├── src/
│   ├── agent/             # Companion logic & tools
│   │   ├── companion.py    # CompanionAgent class
│   │   └── tools.py       # Memory & side-effect tools
│   ├── llm/               # model initialization
│   ├── prompts/           # System & onboarding prompts
│   └── common/            # Logger & exceptions
├── Dockerfile              # uv-based container setup
└── README.md
```

## 🚦 Getting Started

### Prerequisites

- Python 3.12+
- Groq API Key in `.env`

### Local Setup

1. **Clone & Sync**:

   ```bash
   git clone https://github.com/farhanrhine/personal-study-ai-agent.git
   cd personal-study-ai-agent
   uv sync
   ```

2. **Run**:

   ```bash
   uv run streamlit run application.py
   ```

---
*Helping you find your flow, one conversation at a time.*
