# file: ui/web_app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import time
from agent.creator_agent import get_creator_response
from agent.explorer_agent import get_explorer_response
from core.database_handler import add_profile_to_db
from core.database_handler import add_chat_message_to_db
import uuid
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
def rtl_text(text: str) -> str:
    return f'<div style="direction: rtl; text-align: right;">{text}</div>'
st.set_page_config(
    page_title="Cognitive Agent Interface",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="auto"
)
st.markdown("""
<style>
</style>
""", unsafe_allow_html=True)


def get_welcome_message(mode):
    """Returns a dynamic welcome message based on the selected mode."""
    if mode == "Creator Mode":
        return "Welcome to **Creator Mode**. Let's start building a new profile."
    else:
        return "Welcome to **Explorer Mode**. Feel free to ask any questions."

def run_web_app():

    with st.sidebar:
        st.header("✨ Modes")
        selected_mode = st.radio(
            "Select Operating Mode:", ("Creator Mode", "Explorer Mode"),
            key="mode_selection", label_visibility="collapsed"
        )
    if "session_id" not in st.session_state or st.session_state.get("current_mode") != selected_mode:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.current_mode = selected_mode
        welcome_msg=get_welcome_message(selected_mode)
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        #add_chat_message_to_db(st.session_state.session_id, "assistant", welcome_msg)
        st.rerun()

  
    st.title("Cognitive Agent")
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            avatar = "🧑‍🎨" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(rtl_text(message["content"]),unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


    st.markdown('<div class="actions-toolbar">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Restart Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = [{"role": "assistant", "content": get_welcome_message(selected_mode)}]
            st.toast("Chat reset.", icon="🔄")
            st.rerun()

    if selected_mode == "Creator Mode":
        with col2:
            if st.button("✔️ Save Profile", use_container_width=True, type="primary"):
                if "profile_to_save" in st.session_state and st.session_state.profile_to_save:
                    full_chat_history = st.session_state.messages
                    add_profile_to_db(st.session_state.profile_to_save, full_chat_history)
                    st.toast("Profile saved to PostgreSQL!", icon="🎉")
                    del st.session_state.profile_to_save
                    time.sleep(1)
                    st.session_state.messages = [{"role": "assistant", "content": get_welcome_message(selected_mode)}]
                    st.rerun()
                else:
                    st.warning("No completed profile is ready to save.")
    

    if user_input := st.chat_input("Ask me anything...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        assistant_response = ""
        if selected_mode == "Creator Mode":
            Agent_response = get_creator_response(st.session_state.messages)
            assistant_response = Agent_response["text_response"]
            structured_data = Agent_response["structured_data"]
            
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            if structured_data:
    
                st.session_state.profile_to_save = structured_data
                st.info("Profile is ready. Review the data below and click 'Save Profile' to confirm.")
          
        else:
            add_chat_message_to_db(st.session_state.session_id, "user", user_input)
            explorer_agent=get_explorer_response(st.session_state.messages)
            st.session_state.messages.append({'role':'assistant','content':explorer_agent})
            add_chat_message_to_db(st.session_state.session_id, "assistant", explorer_agent)
            
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_web_app()