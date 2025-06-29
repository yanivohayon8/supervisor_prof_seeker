import streamlit as st
import random

def load_intro():
    st.markdown("""
        <style>
            .profect-title {
                text-align: center;
                font-size: 2em;
            }

            .profect-body, .profect-caption {
                color: black;
            }

            @media (prefers-color-scheme: dark) {
                .profect-body, .profect-caption {
                    color: white;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='profect-title'>ProfectMatch 🎓💘🧑‍🏫</h1>", unsafe_allow_html=True)

    st.markdown(
        "<div class='profect-body'>"
        "Are you a Ph.D. or M.Sc. student looking for the right professor to guide your research? "
        "<strong>ProfectMatch</strong> helps you find your perfect match in academia. "
        "<a href='https://www.yanivoha.com/ai-assistant-for-msc-and-ph-d-students'>Learn more</a>."
        "</div>", unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div class='profect-caption'>"
        "💡 This is an experimental system. Please double-check important info. "
        "<strong>Using English is recommended</strong> for now, while Hebrew support continues to improve.<br>"
        "Currently, only researchers from "
        "<a href='https://in.bgu.ac.il/en/natural_science/cs/Pages/default.aspx'>BGU’s Computer Science Department are supported</a>."
        "</div>", unsafe_allow_html=True
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
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                set_feedback(bot,i)


    if prompt := st.chat_input(get_placeholder_()):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

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

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            set_feedback(bot, len(st.session_state.messages)-1)

def get_placeholder_():
    prompts = [
    "What topics or courses do you find most interesting?",
    "Which field of research sounds exciting to you?",
    "Tell me what you'd love to explore during your degree.",
    "What kind of problems do you enjoy solving?",
    ]
    # return random.choice(prompts)
    return prompts[0]