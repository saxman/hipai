# HiPAI - Highly Personalized AI

Modules, tools, examples, and exploration into developing highly personalized AI.

## Overview

HiPAI provides two AI chatbot experiences backed by a persistent vector memory store:

- **Assistant** — an AI friend ("Bruce") that remembers things about you across conversations
- **Clone** — an AI that mimics you, drawing on your stored memories to respond as you would

Both chatbots support multiple LLM backends (Ollama, HuggingFace, Aisuite) and use an MCP server to read and write memories via ChromaDB.

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync

# Create the output directory for runtime artifacts
mkdir output

# Initialize the ChromaDB memory collection (required before first run)
# Open notebooks/01 - Knowledge Base.ipynb and run it to seed initial memories
```

## Running

```bash
# Personal AI assistant
streamlit run streamlit/hipai_assistant.py

# AI clone
streamlit run streamlit/hipai_clone.py
```

Both apps open in your browser. Use the sidebar to switch LLM backend and tune generation parameters. Use **Reset chat** to start a new conversation (memory is preserved across resets).

## Architecture

```
hipai/
├── tools.py        # FastMCP server — exposes memory tools to LLMs
└── paths.py        # Centralized path constants

streamlit/
├── hipai_assistant.py   # Assistant chatbot (Streamlit UI)
└── hipai_clone.py       # Clone chatbot (Streamlit UI)

notebooks/
├── 01 - Knowledge Base.ipynb   # Seed and inspect ChromaDB memories
└── 02 - Memory Usage.ipynb     # Memory retrieval examples

output/             # Runtime artifacts (gitignored)
├── chroma.db                   # ChromaDB vector memory store
├── assistant_chat_history.json
└── clone_chat_history.json
```

The MCP server (`hipai/tools.py`) is launched automatically as a subprocess when a Streamlit app starts. It provides three tools to the LLM: `search_memories`, `add_memories`, and `get_current_date_and_time`.

LLM abstractions are provided by the local [`aimu`](../aimu) package.
