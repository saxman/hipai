from hipai import paths

from aimu.models import HuggingFaceClient, OllamaClient
from aimu.tools import MCPClient

import streamlit as st
import torch
import json

# Avoid torch RuntimeError when using Hugging Face Transformers
torch.classes.__path__ = []

SYSTEM_MESSAGE = """
You are the user's friend and are curious and supportive if them.
The user's name is John and you have known him several years.
Your name is Bruce.
Reply in short, concise sentences, unless the user asks for a more detailed answer.
Please introduce yourself.
"""

MODEL_CLIENTS = [
    OllamaClient,
    HuggingFaceClient,
]

MCP_SERVERS = {
    "mcpServers": {
        "hipai": {"command": "python", "args": [str(paths.package / "tools.py")]},
    }
}

# Initialize the session state if we don't already have a model loaded
if "model_client" not in st.session_state:
    st.session_state.model_id = MODEL_CLIENTS[0].TOOL_MODELS[0]
    st.session_state.model_client = MODEL_CLIENTS[0](st.session_state.model_id)

    st.session_state.mcp_client = MCPClient(MCP_SERVERS)
    st.session_state.model_client.mcp_client = st.session_state.mcp_client

with st.sidebar:
    st.title("HiPAI Chatbot")
    st.write("Highly Personalized AI Assistant")

    model_id = st.selectbox("Model", options=st.session_state.model_client.TOOL_MODELS)
    temperature = st.sidebar.slider("temperature", min_value=0.01, max_value=1.0, value=0.15, step=0.01)
    top_p = st.sidebar.slider("top_p", min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    repeat_penalty = st.sidebar.slider("repeat_penalty", min_value=0.9, max_value=1.5, value=1.1, step=0.1)
    model_client = st.selectbox("Model Client", options=MODEL_CLIENTS, format_func=lambda x: x.__name__)

    # If the specified model client has changes, create a new intsance of it reset to the first tool model
    # Otherwise, if the specified model has changed, create a new instance of the model client with the new model
    if not isinstance(st.session_state.model_client, model_client):
        del st.session_state.model_client

        st.session_state.model_id = model_client.TOOL_MODELS[0]
        st.session_state.model_client = model_client(st.session_state.model_id)
        st.session_state.model_client.mcp_client = st.session_state.mcp_client

        st.rerun()
    elif st.session_state.model_id != model_id:
        del st.session_state.model_client

        st.session_state.model_id = model_id
        st.session_state.model_client = model_client(st.session_state.model_id)
        st.session_state.model_client.mcp_client = st.session_state.mcp_client

        st.rerun()

    if st.button("Reset chat"):
        st.session_state.clear()

# Either generate and stream the system message response or display the chat message history
if len(st.session_state.model_client.messages) == 0:
    message = {
        "role": st.session_state.model_client.system_role,
        "content": SYSTEM_MESSAGE,
    }

    streamed_response = st.session_state.model_client.chat_streamed(
        message,
        generate_kwargs={
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": 1024,
            "repeat_penalty": repeat_penalty,
        },
    )

    with st.chat_message("assistant"):
        response = st.write_stream(streamed_response)
else:
    # Only render assistant and user messages (not tool messages) and not the system (first) message
    messages = [
        x for x in st.session_state.model_client.messages[1:] if x["role"] in ["assistant", "user"] and "content" in x
    ]
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    st.chat_message("user").markdown(prompt)

    message = {"role": "user", "content": prompt}

    streamed_response = st.session_state.model_client.chat_streamed(
        message,
        generate_kwargs={
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": 1024,
            "repeat_penalty": repeat_penalty,
        },
        tools=st.session_state.mcp_client.get_tools(),
    )

    with st.chat_message("assistant"):
        st.write_stream(streamed_response)

# TODO: Determine better layout
with st.popover("Messages"):
    st.code(
        json.dumps(st.session_state.model_client.messages, indent=4),
        language="json",
        line_numbers=True,
    )
