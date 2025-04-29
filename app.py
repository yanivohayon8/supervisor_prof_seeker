import streamlit as st
from src.chatbots.simple import SimpleRAGChatbot
from src.vector_store_loaders.faiss_loader import load_faiss_indexed
from src.api_utils import get_llm_openai
from src.utils import load_chatbot_settings
from src.GUI.bird_eye_graph import load_bird_eye_graph
from src.GUI.core import load_chat,load_intro
from src.consts import BIRD_EYE_GRAPH_DATA

load_bird_eye_graph(BIRD_EYE_GRAPH_DATA)

vector_store = load_faiss_indexed()
bot_settings = load_chatbot_settings()
llm = get_llm_openai(bot_settings.get("model_name"))
bot = SimpleRAGChatbot(llm,vector_store)
bot_config = bot.get_config()

load_intro()
load_chat(bot,bot_config)