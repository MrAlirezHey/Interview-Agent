
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import time
import uuid
import logging
from agent.creator_agent import get_creator_response
from agent.explorer_agent_langcahin import agent_executor
from core.database_handler import add_profile_to_db, add_chat_message_to_db
from langchain_core.messages import AIMessage, HumanMessage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

st.set_page_config(
    page_title="Cognitive Agent Interface",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="auto"
)
st.markdown("""

""", unsafe_allow_html=True)


def get_welcome_message(mode):
    """Returns a dynamic welcome message based on the selected mode."""
    if mode == "Creator Mode":
        return "Welcome to **Creator Mode**. Let's start building a new profile."
    else:
        return "Welcome to **Explorer Mode**. Feel free to ask any questions."

def run_web_app():
    # --- Sidebar and State Management ---
    with st.sidebar:
        st.header("✨ Modes")
        selected_mode = st.radio(
            "Select Operating Mode:", ("Creator Mode", "Explorer Mode"),
            key="mode_selection", label_visibility="collapsed"
        )
    
    if "session_id" not in st.session_state or st.session_state.get("current_mode") != selected_mode:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.current_mode = selected_mode
        welcome_msg = get_welcome_message(selected_mode)
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        add_chat_message_to_db(st.session_state.session_id, "assistant", welcome_msg)
        st.rerun()

    # --- Main Chat Interface ---
    st.title("Cognitive Agent")
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            avatar = "🧑‍🎨" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Actions Toolbar ---
    st.markdown('<div class="actions-toolbar">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Restart Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            welcome_msg = get_welcome_message(selected_mode)
            st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
            add_chat_message_to_db(st.session_state.session_id, "assistant", welcome_msg)
            st.toast("Chat reset.", icon="🔄")
            st.rerun()
    with col2:
        if st.button("✔️ Save Profile", use_container_width=True, type="primary"):
            if selected_mode == "Creator Mode":
                if "profile_to_save" in st.session_state and st.session_state.profile_to_save:
                    full_chat_history = st.session_state.messages
                    add_profile_to_db(st.session_state.profile_to_save, full_chat_history)
                    st.toast("Profile and its chat history saved to PostgreSQL!", icon="🎉")
                    del st.session_state.profile_to_save
                    time.sleep(1)
                    st.session_state.messages = [{"role": "assistant", "content": get_welcome_message(selected_mode)}]
                    st.rerun()
                else:
                    st.warning("No completed profile is ready to save.")
            else:
                st.toast("Save is for Creator Mode only.", icon="⚠️")

    # --- Main Logic for Handling User Input ---
    if user_input := st.chat_input("Ask me anything...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        add_chat_message_to_db(st.session_state.session_id, "user", user_input)
        
        assistant_response = ""
        if selected_mode == "Creator Mode":
            # منطق Creator Mode بدون تغییر باقی می‌ماند
            response_data = get_creator_response(st.session_state.messages)
            assistant_response = response_data["text_response"]
            structured_data = response_data["structured_data"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            add_chat_message_to_db(st.session_state.session_id, "assistant", assistant_response)
            if structured_data:
                st.session_state.profile_to_save = structured_data
                st.info("Profile is ready. Review and click 'Save Profile'.")
        
        else:  # --- CHANGE 2: THIS BLOCK NOW USES LANGCHAIN ---
            # تاریخچه پیام‌ها را به فرمت مورد نیاز LangChain تبدیل می‌کنیم
            lc_chat_history = []
            # از پیام دوم به بعد را می‌گیریم چون پیام اول خوش‌آمدگویی است و در حافظه Agent مدیریت می‌شود
            for msg in st.session_state.messages[1:]: 
                if msg["role"] == "assistant":
                    lc_chat_history.append(AIMessage(content=msg["content"]))
                else:
                    lc_chat_history.append(HumanMessage(content=msg["content"]))
            
            
            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": lc_chat_history
            })
            assistant_response = response["output"]
            
            st.session_state.messages.append({'role':'assistant','content':assistant_response})
            add_chat_message_to_db(st.session_state.session_id, "assistant", assistant_response)
            
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    run_web_app()