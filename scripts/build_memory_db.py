#!/usr/bin/env python3
"""Build a ChromaDB memory database from a file of facts (one fact per line)."""

import sys
import argparse
import chromadb

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from hipai import paths

KNOWLEDGE_BASE_PATH = str(paths.output / "chroma.db")
KNOWLEDGE_BASE_ID = "memories"


def load_facts(file_path: str) -> list[str]:
    with open(file_path) as f:
        return [line.strip() for line in f if line.strip()]


def add_facts(facts: list[str]) -> None:
    client = chromadb.PersistentClient(path=KNOWLEDGE_BASE_PATH)
    collection = client.get_or_create_collection(name=KNOWLEDGE_BASE_ID)
    collection.add(documents=facts, ids=[str(hash(fact)) for fact in facts])


def main():
    parser = argparse.ArgumentParser(description="Load facts into the HiPAI memory database.")
    parser.add_argument("file", help="Path to a text file with one fact per line")
    args = parser.parse_args()

    facts = load_facts(args.file)
    if not facts:
        print("No facts found in file.")
        sys.exit(1)

    paths.output.mkdir(exist_ok=True)
    add_facts(facts)
    print(f"Added {len(facts)} facts to {KNOWLEDGE_BASE_PATH}")


if __name__ == "__main__":
    main()
