# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HiPAI (Highly Personalized AI) is a framework for building personalized AI chatbot experiences. It includes two Streamlit-based chat applications backed by a vector memory store, exposed via MCP (Model Context Protocol) servers.

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run the personal AI assistant chatbot
streamlit run web/hipai_assistant.py

# Run the AI clone chatbot (mimics the user)
streamlit run web/hipai_clone.py

# Run the local MCP server standalone
python hipai/tools.py

# Seed the memory store from a text file of facts (one per line)
python scripts/build_memory_db.py <path/to/facts.txt>
```

Linting uses ruff (configured in `pyproject.toml`): line length 120, target Python 3.9+.

## Architecture

### Key dependency: `aimu`

The `aimu` package (local editable install from `../aimu`) provides the core abstractions used throughout:
- `aimu.models`: `OllamaClient`, `HuggingFaceClient`, `AisuiteClient` — unified LLM interface with tool-use support
- `aimu.tools.client`: `MCPClient` — connects Streamlit apps to MCP servers
- `aimu.tools.servers`: MCP server exposing `search_memories` and `add_memories` tools (backed by `aimu.memory`)
- `aimu.memory`: `MemoryStore` — vector memory persistence
- `aimu.history`: `ConversationManager` — persists conversation history as JSON

### MCP Servers

Two MCP servers are used:

1. **`aimu.tools.servers`** (from the `aimu` package) — the primary memory server, providing `search_memories` and `add_memories` tools to LLMs. Both Streamlit apps connect to this server.

2. **`hipai/tools.py`** (local FastMCP server) — utility server providing `get_current_date_and_time` only. Memory tools were migrated to the `aimu` package.

Both servers are launched as subprocesses by `MCPClient` when a Streamlit app starts.

### Streamlit Apps (`web/`)

Both apps share identical structure — the only differences are the system message and sidebar title:
- `web/hipai_assistant.py` — AI friend persona ("Bruce"), imports `MCPClient` from `aimu.tools.client`
- `web/hipai_clone.py` — User clone persona, imports `MCPClient` from `aimu.tools`

Both apps save chat history to `output/chat_history.json`.

App initialization flow:
1. On first render, create model client + MCP client, load last conversation from `ConversationManager`
2. If no prior messages exist, stream an AI-generated greeting
3. Sidebar allows switching model client type (Ollama/HuggingFace/Aisuite) and model — switching creates a new client instance and calls `st.rerun()`
4. "Reset chat" creates a new `ConversationManager` conversation and clears session state

### Paths (`hipai/paths.py`)

Centralized path constants: `root`, `data`, `tests`, `package`, `output`. All file I/O should use these rather than hardcoded paths.

### Output directory

All runtime artifacts go to `output/` (gitignored): `memory_store/` (vector store written by `MemoryStore`), `chat_history.json`. This directory must exist before running the apps.
