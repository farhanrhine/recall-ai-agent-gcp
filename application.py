import streamlit as st
from src.agent.companion import CompanionAgent
from dotenv import load_dotenv
import json
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

def main():
    st.set_page_config(page_title="Personal AI Agent", page_icon="🤖", layout="wide")

    if "agent" not in st.session_state:
        st.session_state.agent = CompanionAgent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None

    st.title("🤖 Personal AI Agent")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Display chat messages
        for message in st.session_state.messages:
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            with st.chat_message(role):
                st.markdown(message.content)

        # Chat input
        if prompt := st.chat_input("Talk to your agent..."):
            st.session_state.messages.append(HumanMessage(content=prompt))
            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                with st.spinner("Thinking..."):
                    # Pass full history to agent
                    new_messages = st.session_state.agent.chat(st.session_state.messages)
                    
                    # Filter for only the new AI and Tool outputs
                    for msg in new_messages:
                        if isinstance(msg, AIMessage) and msg.content:
                            st.session_state.messages.append(msg)
                            with st.chat_message("assistant"):
                                st.markdown(msg.content)
                        
                        elif msg.type == "tool":
                            # Process quiz tool output
                            try:
                                data = json.loads(msg.content)
                                if isinstance(data, list) and len(data) > 0 and "question" in data[0]:
                                    st.session_state.current_quiz = data
                                    st.success("New quiz generated! Ready for review.")
                            except:
                                pass
            except Exception as e:
                st.error(f"Agent Error: {e}")

    with col2:
        st.header("🎯 Assessment")
        
        if st.session_state.current_quiz:
            st.subheader("Quiz")
            score = 0
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.current_quiz):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    choice = st.radio(f"Options for Q{i+1}", q['options'], key=f"q_{i}")
                    if choice == q['correct_answer']:
                        score += 1
                
                submitted = st.form_submit_button("Submit")
                if submitted:
                    st.success(f"Score: {score}/{len(st.session_state.current_quiz)}")
            
            if st.button("Clear Quiz"):
                st.session_state.current_quiz = None
                st.rerun()
        else:
            st.info("Ask for a quiz on any topic to start an assessment.")

    # Sidebar reset
    if st.sidebar.button("Clear History"):
        st.session_state.messages = []
        st.session_state.current_quiz = None
        st.rerun()

if __name__ == "__main__":
    main()
