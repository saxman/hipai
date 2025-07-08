from hipai import paths

from fastmcp import FastMCP
import chromadb

KNOWLEDGE_BASE_PATH = str(paths.data / "chroma.db")
KNOWLEDGE_BASE_ID = "memory"

mcp = FastMCP("HiPAI MCP Server")


@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"


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
        memories: A list of memories to add for the user.
    """

    client = chromadb.PersistentClient(path=KNOWLEDGE_BASE_PATH)
    collection = client.get_collection(name=KNOWLEDGE_BASE_ID)

    collection.add(
        documents=memories,
        ids=[str(hash(x)) for x in memories]
    )

@mcp.tool
def get_time_and_date() -> str:
    """
    Get the current time and date.

    Returns:
        The current time and date as a string.
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run()
