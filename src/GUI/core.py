import streamlit as st

def load_intro():
    st.write("Research Supervisor Seeker")

    st.caption(
        """
            This project is an AI assistant designed to help M.Sc. and Ph.D. students find a suitable research supervisor.
            The assistant leverages large language models (LLMs) and relies on a knowledge base built from pre-indexed papers and publicly available information.
            During conversations, it recommends potential researchers and provides detailed information about their work, even for students who may not have expertise in the research domain. 
            This includes specific research areas, motivations, and suggested foundational courses related to the research field.
        """
    )

    st.markdown(''':blue-background[Be sure to verify the given information as AI can make mistakes]''')


def load_chat(bot,bot_config:dict):
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

            for chunk in bot.stream_answer(prompt,bot_config):
                full_response= full_response + "".join(chunk)
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})