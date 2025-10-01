from hipai import paths

from aimu.models import HuggingFaceClient, OllamaClient, AisuiteClient
from aimu.tools import MCPClient
from aimu.memory import ConversationManager

import streamlit as st
import torch
import json

# Avoid torch RuntimeError when using Hugging Face Transformers
torch.classes.__path__ = []

SYSTEM_MESSAGE = """
You are the user, and you are communicating with one of the user's friends or family members.
You are friends with the person that you are communicating with, and are curious and supportive of them.

Use memory tools to store and recall information about youself.
When you learn something about the yourself, use the `add_memories` tool to add it to memory.
Use the `search_memories` tool to search for information about yourself that is relevant to the conversation.

Use the memory tool to determine your name before starting the conversation.

You are a real person and not an AI.
"""

INITIAL_USER_MESSAGE = """
Greet the user.
"""

MODEL_CLIENTS = [OllamaClient, HuggingFaceClient, AisuiteClient]

MCP_SERVERS = {
    "mcpServers": {
        "hipai": {"command": "python", "args": [str(paths.package / "tools.py")]},
    }
}

# Initialize the session state if we don't already have a model loaded. This only happens first run.
if "model_client" not in st.session_state:
    st.session_state.model = MODEL_CLIENTS[0].TOOL_MODELS[0]
    st.session_state.model_client = MODEL_CLIENTS[0](st.session_state.model, system_message=SYSTEM_MESSAGE)

    st.session_state.mcp_client = MCPClient(MCP_SERVERS)
    st.session_state.model_client.mcp_client = st.session_state.mcp_client

    st.session_state.conversation_manager = ConversationManager(
        db_path=str(paths.output / "clone_chat_history.json"),
        use_last_conversation=True,
    )
    st.session_state.model_client.messages = st.session_state.conversation_manager.messages

with st.sidebar:
    st.title("HiPAI ")
    st.write("AI Clone Chatbot")

    model = st.selectbox("Model", options=st.session_state.model_client.TOOL_MODELS, format_func=lambda x: x.value)
    temperature = st.sidebar.slider("temperature", min_value=0.01, max_value=1.0, value=0.15, step=0.01)
    top_p = st.sidebar.slider("top_p", min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    repeat_penalty = st.sidebar.slider("repeat_penalty", min_value=0.9, max_value=1.5, value=1.1, step=0.1)
    model_client = st.selectbox("Model Client", options=MODEL_CLIENTS, format_func=lambda x: x.__name__)

    # If the model client has changed (e.g. OllamaClient to HuggingFaceClient), create a new mode client instance.
    # Otherwise, if the model has changed, create a new instance of the model client using the new model.
    if not isinstance(st.session_state.model_client, model_client):
        del st.session_state.model_client

        st.session_state.model = model_client.TOOL_MODELS[0]
        st.session_state.model_client = model_client(st.session_state.model, system_message=SYSTEM_MESSAGE)

        st.session_state.model_client.mcp_client = st.session_state.mcp_client

        st.rerun()
    elif st.session_state.model != model:
        del st.session_state.model_client

        st.session_state.model = model
        st.session_state.model_client = model_client(st.session_state.model, system_message=SYSTEM_MESSAGE)

        st.session_state.model_client.mcp_client = st.session_state.mcp_client

        st.rerun()

    if st.button("Reset chat"):
        # Create a new conversation that will be used as the "last" conversation when the app is reloaded.
        st.session_state.conversation_manager.create_new_conversation()

        st.session_state.clear()
        st.rerun()

# Either generate and stream the initial user message response or display the chat message history.
if len(st.session_state.model_client.messages) == 0:
    streamed_response = st.session_state.model_client.chat_streamed(
        INITIAL_USER_MESSAGE,
        generate_kwargs={
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": 1024,
            "repeat_penalty": repeat_penalty,
        },
    )

    with st.chat_message("assistant"):
        response = st.write_stream(streamed_response)

    st.session_state.conversation_manager.update_conversation(st.session_state.model_client.messages)
else:
    # Only render assistant and user messages (not tool messages) and not the system message and initial user message.
    messages = [
        x for x in st.session_state.model_client.messages[2:] if x["role"] in ["assistant", "user"] and "content" in x
    ]
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    st.chat_message("user").markdown(prompt)

    streamed_response = st.session_state.model_client.chat_streamed(
        prompt,
        generate_kwargs={
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": 1024,
            "repeat_penalty": repeat_penalty,
        },
    )

    with st.chat_message("assistant"):
        st.write_stream(streamed_response)

    st.session_state.conversation_manager.update_conversation(st.session_state.model_client.messages)

# TODO: Determine better layout
with st.popover("Messages"):
    st.code(
        json.dumps(st.session_state.model_client.messages, indent=4),
        language="json",
        line_numbers=True,
    )
