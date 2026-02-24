import streamlit as st
from src.agent.companion import CompanionAgent
from dotenv import load_dotenv
import os
import json
from langchain_core.messages import AIMessage

load_dotenv()

def main():
    st.set_page_config(page_title="Personal AI Agent Companion", page_icon="🤖", layout="wide")

    if "agent" not in st.session_state:
        st.session_state.agent = CompanionAgent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None

    st.title("🤖 Personal AI Agent Companion")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Display chat messages
        for message in st.session_state.messages:
            role = "user" if message["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("How can I help you today?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                with st.spinner("Processing..."):
                    # Get list of new messages
                    new_messages = st.session_state.agent.chat(prompt)
                    
                    for msg in new_messages:
                        if msg.type == "ai" and msg.content:
                            st.session_state.messages.append({"role": "assistant", "content": msg.content})
                            with st.chat_message("assistant"):
                                st.markdown(msg.content)
                        
                        elif msg.type == "tool":
                            # Check if this tool output contains a quiz
                            if msg.content and not msg.content.startswith("Error"):
                                try:
                                    data = json.loads(msg.content)
                                    if isinstance(data, list) and len(data) > 0 and "question" in data[0]:
                                        st.session_state.current_quiz = data
                                        st.success("New quiz generated! Check the sidebar.")
                                except:
                                    pass
            except Exception as e:
                st.error(f"Agent Error: {e}")

    with col2:
        st.header("🧠 Agent Memory & Tasks")
        
        # Profile Data
        if os.path.exists("user_profile.json"):
            with open("user_profile.json", "r") as f:
                profile = json.load(f)
                if profile:
                    st.subheader("User Profile")
                    for k, v in profile.items():
                        st.write(f"**{k.replace('_', ' ').capitalize()}**: {v}")
                else:
                    st.info("Agent is still learning about you...")
        
        st.markdown("---")

        # Quiz Display
        if st.session_state.current_quiz:
            st.subheader("📝 Practice Quiz")
            score = 0
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.current_quiz):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    choice = st.radio(f"Options for Q{i+1}", q['options'], key=f"q_{i}")
                    if choice == q['correct_answer']:
                        score += 1
                
                submitted = st.form_submit_button("Submit Answers")
                if submitted:
                    st.success(f"You scored {score}/{len(st.session_state.current_quiz)}!")
                    if score == len(st.session_state.current_quiz):
                        st.balloons()
            
            if st.button("Clear Quiz"):
                st.session_state.current_quiz = None
                st.rerun()

        # Reset
        if st.sidebar.button("Reset Everything"):
            st.session_state.messages = []
            st.session_state.current_quiz = None
            if os.path.exists("user_profile.json"):
                os.remove("user_profile.json")
            st.rerun()

if __name__ == "__main__":
    main()
