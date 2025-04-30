import streamlit as st

def load_intro():
    st.title("AI Assistant for Seeking a Research Supervisor :sunglasses:")

    st.markdown(
        """
            This project is an AI assistant designed to help M.Sc. and Ph.D. students find a suitable research supervisor.
            The assistant leverages large language models (LLMs) and relies on a knowledge base built from pre-indexed papers and publicly available information.
            During conversations, it recommends potential researchers and provides detailed information about their work, even for students who may not have expertise in the research domain. 
            This includes specific research areas, motivations, and suggested foundational courses related to the research field.
        """
    )

    st.caption(
        """
            Currently, the AI assistant supports researchers only from the Computer Science Department at Ben-Gurion University.       
        
            For the full list of faculty members, visit: https://in.bgu.ac.il/en/natural_science/cs/Pages/default.aspx

            :blue-background[Please verify the information, as AI-generated content may contain errors.]
        """
    )

    st.markdown('''''')


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