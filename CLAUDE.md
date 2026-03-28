# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HiPAI (Highly Personalized AI) is a framework for building personalized AI chatbot experiences. It includes two Streamlit-based chat applications backed by a ChromaDB vector memory store, exposed via an MCP (Model Context Protocol) server.

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run the personal AI assistant chatbot
streamlit run streamlit/hipai_assistant.py

# Run the AI clone chatbot (mimics the user)
streamlit run streamlit/hipai_clone.py

# Run the MCP server standalone
python hipai/tools.py
```

Linting uses ruff (configured in `pyproject.toml`): line length 120, target Python 3.9+.

## Architecture

### Key dependency: `aimu`

The `aimu` package (local editable install from `../aimu`) provides the core abstractions used throughout:
- `aimu.models`: `OllamaClient`, `HuggingFaceClient`, `AisuiteClient` — unified LLM interface with tool-use support
- `aimu.tools`: `MCPClient` — connects Streamlit apps to the MCP server
- `aimu.history`: `ConversationManager` — persists conversation history as JSON

### MCP Memory Server (`hipai/tools.py`)

A FastMCP server exposing three tools to LLMs:
- `search_memories` — queries ChromaDB vector store for relevant user memories
- `add_memories` — stores new facts about the user in ChromaDB
- `get_current_date_and_time` — utility for current timestamp

ChromaDB persists to `output/chroma.db`. The collection name is `"memories"`. The MCP server is launched as a subprocess by Streamlit apps via `MCPClient`.

### Streamlit Apps (`streamlit/`)

Both apps share identical structure — the only differences are the system message and the chat history file path:
- `hipai_assistant.py` — AI friend persona ("Bruce"), history at `output/assistant_chat_history.json`
- `hipai_clone.py` — User clone persona, history at `output/clone_chat_history.json`

App initialization flow:
1. On first render, create model client + MCP client, load last conversation from `ConversationManager`
2. If no prior messages exist, stream an AI-generated greeting
3. Sidebar allows switching model client type (Ollama/HuggingFace/Aisuite) and model — switching creates a new client instance and calls `st.rerun()`
4. "Reset chat" creates a new `ConversationManager` conversation and clears session state

### Paths (`hipai/paths.py`)

Centralized path constants: `root`, `data`, `tests`, `package`, `output`. All file I/O should use these rather than hardcoded paths.

### Output directory

All runtime artifacts go to `output/` (gitignored): `chroma.db`, `assistant_chat_history.json`, `clone_chat_history.json`. This directory must exist before running the apps.
