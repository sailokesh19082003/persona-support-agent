"""
Streamlit chat UI for the Persona-Adaptive Support Agent.

Run with:
    streamlit run app.py

Shows, for every turn: the user message, detected persona (+confidence),
retrieved sources (+scores), the generated response, and escalation status
- plus a sidebar for knowledge-base management and lightweight session
analytics (persona distribution, escalation count).
"""
import json

import streamlit as st

from src import config
from src.agent import SupportAgent

st.set_page_config(page_title=config.APP_TITLE, page_icon="🎧", layout="wide")

PERSONA_BADGE = {
    "Technical Expert": "🛠️",
    "Frustrated User": "💢",
    "Business Executive": "📊",
}


@st.cache_resource
def get_agent():
    return SupportAgent()


def render_sidebar(agent: SupportAgent):
    with st.sidebar:
        st.header(config.APP_TITLE)
        st.caption("Persona-Adaptive Customer Support Agent")

        if not config.GEMINI_API_KEY:
            st.warning(
                "GEMINI_API_KEY not set. Running in fallback/dev mode "
                "(heuristic persona classification, placeholder responses). "
                "Add it to your .env file for full functionality."
            )

        st.subheader("Knowledge Base")
        stats = agent.kb_stats()
        st.metric("Indexed chunks", stats["chunk_count"])

        if stats["chunk_count"] == 0:
            st.error("Knowledge base is empty.")
        if st.button("🔄 (Re)build Knowledge Base Index", use_container_width=True):
            with st.spinner("Loading, chunking, and embedding documents..."):
                progress_bar = st.progress(0.0)

                def progress(i, total):
                    progress_bar.progress(i / total)

                count = agent.pipeline.ingest_from_data_dir(progress_callback=progress)
            st.success(f"Indexed {count} chunks.")
            st.rerun()

        st.divider()
        st.subheader("Session Analytics")
        dist = agent.memory.persona_distribution()
        if dist:
            st.bar_chart(dist)
        else:
            st.caption("No messages yet this session.")
        st.metric("Escalations this session", agent.memory.escalation_count())

        st.divider()
        st.subheader("Settings (read-only)")
        st.code(
            f"Chat model: {config.CHAT_MODEL}\n"
            f"Embedding model: {config.EMBEDDING_MODEL}\n"
            f"Top-K retrieval: {config.TOP_K}\n"
            f"Confidence threshold: {config.RETRIEVAL_CONFIDENCE_THRESHOLD}",
            language="text",
        )

        if st.button("Clear conversation", use_container_width=True):
            agent.memory.clear()
            st.session_state.chat_history = []
            st.rerun()


def render_turn(role: str, content, result: dict = None):
    with st.chat_message(role):
        if role == "user":
            st.markdown(content)
            return

        badge = PERSONA_BADGE.get(result["persona"], "🎧")
        st.markdown(f"**{badge} Detected persona:** {result['persona']} "
                     f"(confidence: {result.get('persona_confidence')})")

        if result["retrieved"]:
            with st.expander(f"📚 Retrieved sources ({len(result['retrieved'])})"):
                for c in result["retrieved"]:
                    st.markdown(f"- `{c['source']}` — *{c['section']}* — score `{c['score']}`")
        else:
            st.caption("📚 No relevant sources retrieved.")

        if result["escalated"]:
            st.error(f"🚨 Escalated to human agent — reasons: {', '.join(result['escalation_reasons'])}")
        else:
            st.success("✅ Resolved by agent")

        st.markdown(result["response"])

        if result["escalated"] and result["handoff_summary"]:
            with st.expander("🧾 Human Handoff Summary (JSON)"):
                st.code(json.dumps(result["handoff_summary"], indent=2), language="json")


def main():
    agent = get_agent()
    render_sidebar(agent)

    st.title(f"🎧 {config.APP_TITLE}")
    st.caption("Ask a support question — the agent detects your persona, retrieves "
               "relevant docs, and adapts its tone accordingly.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for entry in st.session_state.chat_history:
        render_turn(entry["role"], entry["content"], entry.get("result"))

    user_input = st.chat_input("Type your support question...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        render_turn("user", user_input)

        with st.spinner("Classifying persona, retrieving context, generating response..."):
            result = agent.handle_message(user_input)

        st.session_state.chat_history.append({"role": "assistant", "content": None, "result": result})
        render_turn("assistant", None, result)


if __name__ == "__main__":
    main()
