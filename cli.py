"""
Command-line chatbot interface.

This satisfies the assignment's minimum UI requirement ("Interactive
command-line chatbot"). Run with:

    python cli.py

Type 'exit' or 'quit' to stop. Type 'stats' to see knowledge base /
session analytics at any time.
"""
import json
import logging

from src import config
from src.agent import SupportAgent

logging.basicConfig(level=logging.WARNING)  # keep CLI output clean


def _print_banner():
    print("=" * 70)
    print(f"  {config.APP_TITLE} - CLI Mode")
    print("=" * 70)
    print("Type your support question below. Commands: 'stats', 'exit'.\n")


def _print_turn(result: dict):
    print(f"\n[Persona detected]: {result['persona']} "
          f"(confidence: {result.get('persona_confidence')})")

    if result["retrieved"]:
        print("[Retrieved sources]:")
        for c in result["retrieved"]:
            print(f"   - {c['source']} ({c['section']})  score={c['score']}")
    else:
        print("[Retrieved sources]: none")

    status = "ESCALATED TO HUMAN" if result["escalated"] else "Resolved by agent"
    print(f"[Escalation status]: {status}")
    if result["escalated"]:
        print(f"[Escalation reasons]: {', '.join(result['escalation_reasons'])}")

    print(f"\nAgent: {result['response']}\n")

    if result["escalated"] and result["handoff_summary"]:
        print("--- Human Handoff Summary ---")
        print(json.dumps(result["handoff_summary"], indent=2))
        print("------------------------------\n")


def main():
    agent = SupportAgent()
    stats = agent.kb_stats()

    if stats["chunk_count"] == 0:
        print(f"WARNING: knowledge base collection '{stats['collection']}' is empty.")
        print("Run 'python ingest.py' first to build the vector index.\n")

    _print_banner()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if user_input.lower() == "stats":
            print(f"\nKnowledge base: {agent.kb_stats()}")
            print(f"Session persona distribution: {agent.memory.persona_distribution()}")
            print(f"Session escalations: {agent.memory.escalation_count()}\n")
            continue

        result = agent.handle_message(user_input)
        _print_turn(result)


if __name__ == "__main__":
    main()
