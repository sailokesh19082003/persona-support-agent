"""
Lightweight in-memory conversation history.

Used for two things:
1. Feeding the last few turns into the escalation logic (e.g. detecting
   "repeated frustration over several consecutive turns").
2. Building a richer human-handoff summary that includes prior turns,
   not just the single message that triggered escalation.

This is intentionally simple (a plain Python list) rather than a database,
since the assignment only requires session-level multi-turn awareness, not
durable cross-session storage. Swapping in SQLite/Redis later is a one-line
change at the call site (see README "Known Limitations").
"""
from datetime import datetime, timezone


class ConversationMemory:
    def __init__(self):
        self.turns = []  # list of dicts, oldest first

    def add_turn(self, user_message: str, persona: str, escalated: bool, response: str = None):
        self.turns.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": user_message,
            "persona": persona,
            "escalated": escalated,
            "response": response,
        })

    def recent(self, n: int = 5) -> list[dict]:
        return self.turns[-n:]

    def consecutive_persona_count(self, persona: str) -> int:
        """How many turns in a row (most recent first) match `persona`."""
        count = 0
        for turn in reversed(self.turns):
            if turn["persona"] == persona:
                count += 1
            else:
                break
        return count

    def persona_distribution(self) -> dict:
        """Simple analytics: counts per persona across the whole session."""
        dist = {}
        for turn in self.turns:
            dist[turn["persona"]] = dist.get(turn["persona"], 0) + 1
        return dist

    def escalation_count(self) -> int:
        return sum(1 for t in self.turns if t["escalated"])

    def clear(self):
        self.turns = []
