from hipai import paths

from fastmcp import FastMCP
import chromadb
from datetime import datetime

KNOWLEDGE_BASE_PATH = str(paths.output / "chroma.db")
KNOWLEDGE_BASE_ID = "memories"

mcp = FastMCP("HiPAI MCP Server")


@mcp.tool
def search_memories(search_request: str) -> str:
    """
    Search for memories about the user.

    Args:
        search_request: Information about the user that's relevant to the conversation.

    Returns:
        Information about the user that's relevant to the conversation.
    """

    client = chromadb.PersistentClient(path=KNOWLEDGE_BASE_PATH)
    collection = client.get_collection(name=KNOWLEDGE_BASE_ID)
    results = collection.query(query_texts=[search_request], n_results=10)

    memories = [x for x in results["documents"][0]]

    return "\n".join(memories)


@mcp.tool
def add_memories(memories: list[str]) -> None:
    """
    Add memories about the user.

    Args:
        memories: A list of memories, as strings, to save about the user.
    """

    client = chromadb.PersistentClient(path=KNOWLEDGE_BASE_PATH)
    collection = client.get_collection(name=KNOWLEDGE_BASE_ID)

    collection.add(documents=memories, ids=[str(hash(x)) for x in memories])


@mcp.tool
def get_current_date_and_time() -> str:
    """
    Get the current time and date.

    Returns:
        The current time and date as a string.
    """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run()
