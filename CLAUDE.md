# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                                         # Install dependencies
streamlit run web/hipai_assistant.py            # Run personal assistant chatbot
streamlit run web/hipai_clone.py                # Run AI clone chatbot
python hipai/tools.py                           # Run MCP server standalone
ruff check .                                    # Lint (120-char line length, configured in pyproject.toml)
```

## Architecture

HiPAI provides two Streamlit chat UIs backed by vector memory and an MCP tool server.

**Two Streamlit apps** (`web/`):
- `hipai_assistant.py` — personal AI assistant ("friend" persona) that learns about the user
- `hipai_clone.py` — AI clone that mimics the user when talking to their friends

Both apps share the same pattern:
1. Load chat history from `output/*.json`
2. Build a system prompt with retrieved memories (via MCP tools)
3. Stream responses using an `aimu` model client

**`aimu` (sibling package at `../aimu`)** provides:
- Model clients: `OllamaClient`, `HuggingFaceClient`, `AisuiteClient` — each supports streaming chat with configurable parameters (temperature, top_p, repeat_penalty)
- Chat history utilities (imported as `aimu.history`)

**`hipai/tools.py`** — FastMCP server exposing three tools over the MCP protocol:
- `search_memories(search_request)` — vector similarity search in ChromaDB (returns up to 10 results)
- `add_memories(memories)` — stores new memory documents in ChromaDB
- `get_current_date_and_time()` — returns current timestamp

Both Streamlit apps connect to this server via `MCPClient` at runtime; the MCP server is launched as a subprocess.

**Storage** (all under `output/`, created at runtime):
- `output/memory_store/` — ChromaDB persistent vector store for memories (via `aimu.memory.MemoryStore`)
- `output/assistant_chat_history.json` — assistant conversation history
- `output/clone_chat_history.json` — clone conversation history

**`hipai/paths.py`** centralizes all path constants used across the package.
