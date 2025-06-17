import streamlit as st
from src.chatbots.simple import SimpleRAGChatbot, generate_graph_config
from src.vector_store_loaders.faiss_loader import load_faiss_indexed
from src.api_utils import get_llm_langchain_openai, verify_openai_api_key
from src.utils import load_chatbot_settings
from src.GUI.core import load_chat, load_intro
from src.chatbots.lunary_wrapper import ConversationRecorder


@st.cache_resource
def api_key():
    verify_openai_api_key()

@st.cache_resource
def load_vector_store():
    return load_faiss_indexed()

@st.cache_data
def load_chatbot_settings_cached():
    return load_chatbot_settings()

@st.cache_resource
def load_llm(settings: dict):
    return get_llm_langchain_openai(is_lunary_audit=True, **settings)

st.set_page_config(page_title="ProfectMatch")
api_key()
vector_store = load_vector_store()
llm_settings = load_chatbot_settings_cached()
llm = load_llm(llm_settings.get("ChatOpenAI"))

if "thread_id" not in st.session_state:
    graph_config = generate_graph_config()
    st.session_state["graph_config"] = graph_config
    thread_id = graph_config.get("configurable").get("thread_id")
    st.session_state["thread_id"] = thread_id

    conversation_recorder = ConversationRecorder(thread_id=thread_id, tags=["Web Application"])
    bot = SimpleRAGChatbot(llm, vector_store, st.session_state["graph_config"], converstation_recorder=conversation_recorder)

    st.session_state["bot"] = bot

load_intro()
load_chat(st.session_state.bot)
