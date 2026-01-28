def add_agent_message(state, agent_name, message):
    """Add a message to shared context for inter-agent communication."""
    current_context = state.get("shared_context", "")
    if current_context:
        updated_context = f"{current_context}\n\n[{agent_name}]: {message}"
    else:
        updated_context = f"[{agent_name}]: {message}"
    return updated_context


def get_agent_messages(state, from_agent=None):
    """Retrieve messages from shared context, optionally filtered by agent."""
    context = state.get("shared_context", "")
    if not context:
        return ""

    if from_agent:
        lines = context.split("\n")
        filtered = [line for line in lines if line.startswith(f"[{from_agent}]:")]
        return "\n".join(filtered)

    return context
