# HiPAI - Highly Personalized AI

Modules, tools, examples, and exploration into developing highly personalized AI.

## Overview

HiPAI provides two AI chatbot experiences backed by a persistent vector memory store:

- **Assistant** — an AI friend ("Bruce") that remembers things about you across conversations
- **Clone** — an AI that mimics you, drawing on your stored memories to respond as you would

Both chatbots support multiple LLM backends (Ollama, HuggingFace, Aisuite) and use an MCP server to read and write memories.

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync

# Create the output directory for runtime artifacts
mkdir output

# Initialize the memory store (required before first run)
# Open notebooks/01 - Knowledge Base.ipynb and run it to seed initial memories
```

## Running

```bash
# Personal AI assistant
streamlit run web/hipai_assistant.py

# AI clone
streamlit run web/hipai_clone.py
```

Both apps open in your browser. Use the sidebar to switch LLM backend and tune generation parameters. Use **Reset chat** to start a new conversation (memory is preserved across resets).

## Architecture

```
hipai/
├── tools.py        # FastMCP server — exposes get_current_date_and_time to LLMs
└── paths.py        # Centralized path constants

web/
├── hipai_assistant.py   # Assistant chatbot (Streamlit UI)
└── hipai_clone.py       # Clone chatbot (Streamlit UI)

scripts/
└── build_memory_db.py   # CLI tool to seed the memory store from a text file of facts

notebooks/
├── 01 - Knowledge Base.ipynb   # Seed and inspect the memory store
└── 02 - Memory Usage.ipynb     # Memory retrieval examples

output/             # Runtime artifacts (gitignored)
├── memory_store/               # aimu.memory.MemoryStore vector store
└── chat_history.json           # Conversation history
```

Memory tools (`search_memories`, `add_memories`) are provided by the [`aimu`](../aimu) package via `aimu.tools.servers`. The local MCP server (`hipai/tools.py`) provides only the `get_current_date_and_time` utility. Both MCP servers are launched automatically as subprocesses when a Streamlit app starts.

LLM abstractions are provided by the local [`aimu`](../aimu) package.
