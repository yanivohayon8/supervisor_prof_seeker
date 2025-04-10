import streamlit as st
from src.chatbots.simple import SimpleRAGChatbot
from src.vector_store_loaders.faiss_loader import load_faiss_indexed


vector_store = load_faiss_indexed()
chat_bot = SimpleRAGChatbot(vector_store)
config = chat_bot.get_config()

st.write("Supervisor Seeker")

cap = (
    "This chatbot is designed to help MS.c and Phd students at the Computer Science department to look for a supervisor in Ben-Gurion University. "
    "The chatbot relies on indexing the abstracts of the supervisors papers. \n"
    "Be sure to check for more information at the department website and personal websites of the supervisors. \n" 
    "AI CAN HALLUCINATE AND MAKE MISTAKES."
)

st.caption(cap)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in chat_bot.stream_answer(prompt,config):
            full_response= full_response + chunk + " "
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
