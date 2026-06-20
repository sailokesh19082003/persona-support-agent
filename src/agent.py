"""
Top-level orchestrator: wires together classifier -> retriever -> generator
-> escalation, and keeps conversation memory across turns.

Both app.py (Streamlit) and cli.py call this single function so the actual
"agent workflow" logic exists in exactly one place.
"""
import logging

from src import classifier, generator
from src.memory import ConversationMemory
from src.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)


class SupportAgent:
    def __init__(self):
        self.pipeline = RAGPipeline()
        self.memory = ConversationMemory()

    def handle_message(self, user_message: str) -> dict:
        """
        Run one full turn of the workflow:
            classify persona -> retrieve context -> generate/escalate -> log to memory

        Returns a dict with everything the UI needs to display:
            persona, confidence, reasoning, retrieved (list), response,
            escalated (bool), handoff_summary (dict|None), escalation_reasons (list)
        """
        classification = classifier.classify_persona(user_message)
        persona = classification["persona"]

        retrieved = self.pipeline.retrieve_context(user_message)

        result = generator.generate_response(
            user_query=user_message,
            persona=persona,
            context_chunks=retrieved,
            memory=self.memory,
        )

        self.memory.add_turn(
            user_message=user_message,
            persona=persona,
            escalated=result["escalated"],
            response=result["response"],
        )

        return {
            "persona": persona,
            "persona_confidence": classification.get("confidence"),
            "persona_reasoning": classification.get("reasoning"),
            "retrieved": retrieved,
            "response": result["response"],
            "escalated": result["escalated"],
            "escalation_reasons": result["escalation_reasons"],
            "handoff_summary": result["handoff_summary"],
        }

    def kb_stats(self) -> dict:
        return self.pipeline.stats()
