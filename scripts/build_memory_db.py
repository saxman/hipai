#!/usr/bin/env python3
"""Build the memory store from a file of facts (one fact per line)."""

import argparse

from aimu.memory import MemoryStore
from hipai import paths


def load_facts(file_path: str) -> list[str]:
    with open(file_path) as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser(description="Load facts into the HiPAI memory store.")
    parser.add_argument("file", help="Path to a text file with one fact per line")
    args = parser.parse_args()

    facts = load_facts(args.file)
    if not facts:
        print("No facts found in file.")
        return

    paths.output.mkdir(exist_ok=True)

    store = MemoryStore(persist_path=str(paths.output / "memory_store"))
    for fact in facts:
        store.store_fact(fact)

    print(f"Added {len(facts)} facts to {paths.output / 'memory_store'}")


if __name__ == "__main__":
    main()
