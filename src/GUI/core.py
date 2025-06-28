import streamlit as st

def load_intro():
    st.markdown("<h1 style='text-align: center;'>ProfectMatch 🎓💘🧑‍🏫</h1>", unsafe_allow_html=True)

    st.markdown(
        "Are you a Ph.D. or M.Sc. student looking for the right professor to guide your research? **ProfectMatch** helps you find your perfect match in academia. [Learn more](https://www.yanivoha.com/ai-assistant-for-msc-and-ph-d-students)"
    )

    st.caption(
    """💡 This is an experimental system. Please double-check important info. **Using English is recommended** for now, while Hebrew support continues to improve.  
    Currently, only researchers from [BGU’s Computer Science Department are supported](https://in.bgu.ac.il/en/natural_science/cs/Pages/default.aspx)."""
    )

def set_feedback(bot,msg_index):
    feedback = st.feedback("thumbs",key=msg_index)

    if msg_index > 0:
        if feedback == 1:
            bot.track_positive_feedback(msg_index)
        elif feedback == 0:
            bot.track_negative_feedback(msg_index)
        elif feedback is None:
            bot.track_delete_feedback(msg_index)

def load_chat(bot):
    # Initialize chat history and feedback tracking
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]
    
    # --- Display all messages ---
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show feedback widget for assistant messages
            if message["role"] == "assistant":
                set_feedback(bot,i)


    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response with feedback buttons
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                for chunk in bot.stream_answer(prompt):
                    full_response += "".join(chunk)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = (
                    "⚠️ Oops! Something went wrong while processing your request.\n\n"
                    "Please try again in a moment. If the issue persists, feel free to contact the developer. 🙏"
                )
                message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            set_feedback(bot, len(st.session_state.messages)-1)