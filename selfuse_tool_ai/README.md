# AI Browser Assistant

This module provides a system tray AI assistant with a CustomTkinter UI integrated with OpenAI's API and a retrieval-augmented generation (RAG) memory system. It uses the `chrome-devtools-mcp` tool to control a Chromium browser for tasks such as fetching web pages, automating interactions, and measuring performance.

## Components

- **app.py** – Entry point that sets up the system tray icon and launches the UI.
- **core/** – Contains the underlying components:
  - `mcp_client.py` – Starts and communicates with the `chrome-devtools-mcp` server.
  - `orchestrator.py` – Plans and executes step-by-step tasks using the LLM and MCP.
  - `llm.py` – Wrapper around the OpenAI API for chat and structured planning.
  - `rag.py` – Simple retrieval-augmented generation implementation using Chroma for embeddings and search.
  - `memory.py` – Persists recent conversations to a SQLite database for short-term memory.
- **ui/** – Contains `main_window.py`, a simple CustomTkinter window for displaying tasks and logs.
- **requirements.txt** – Lists Python dependencies required to run the assistant.

## Running

After installing the dependencies (`pip install -r requirements.txt`), you can run `app.py` to start the tray icon and open the assistant window. To control web pages and measure metrics, ensure the `chrome-devtools-mcp` server is installed (via `npm`) and accessible from the Python code.
