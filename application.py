import streamlit as st
from src.agent.companion import CompanionAgent
from dotenv import load_dotenv
import json
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

def main():
    st.set_page_config(page_title="Personal AI Tutor", page_icon="🎓", layout="wide")

    if "agent" not in st.session_state:
        st.session_state.agent = CompanionAgent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "active_quiz" not in st.session_state:
        st.session_state.active_quiz = None

    st.title("🎓 Personal AI Tutor")
    st.caption("Learn anything. Test your knowledge. Master the topic.")
    st.markdown("---")

    col_chat, col_study = st.columns([1.5, 1])

    with col_chat:
        st.subheader("💬 Learning Conversation")
        
        # Chat history container
        chat_placeholder = st.container(height=550)
        
        with chat_placeholder:
            for message in st.session_state.messages:
                if isinstance(message, (HumanMessage, AIMessage)) and message.content:
                    role = "user" if isinstance(message, HumanMessage) else "assistant"
                    with st.chat_message(role):
                        st.markdown(message.content)

        # Chat input
        if prompt := st.chat_input("What do you want to learn today? (e.g. 'Teach me Docker')"):
            st.session_state.messages.append(HumanMessage(content=prompt))
            with chat_placeholder:
                with st.chat_message("user"):
                    st.markdown(prompt)

            try:
                with st.spinner("Preparing lesson..."):
                    new_msgs = st.session_state.agent.chat(prompt)
                    
                    for msg in new_msgs:
                        if isinstance(msg, AIMessage) and msg.content:
                            st.session_state.messages.append(msg)
                            with chat_placeholder:
                                with st.chat_message("assistant"):
                                    st.markdown(msg.content)
                        
                        elif msg.type == "tool":
                            # Check for quiz tool output
                            if isinstance(msg.content, str) and msg.content.startswith("{"):
                                try:
                                    data = json.loads(msg.content)
                                    if data.get("type") == "quiz_data":
                                        st.session_state.active_quiz = data
                                        st.toast("New Quiz Generated!", icon="📝")
                                except:
                                    pass
            except Exception as e:
                st.error(f"Tutor Error: {e}")

    with col_study:
        st.subheader("📝 Study Center")
        
        if st.session_state.active_quiz:
            quiz = st.session_state.active_quiz
            st.info(f"**Topic: {quiz['topic']}**")
            
            score = 0
            user_answers = {}
            
            with st.form("study_center_quiz"):
                for i, q in enumerate(quiz['questions']):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    user_answers[i] = st.radio(f"Options for Q{i+1}", q['options'], key=f"study_q_{i}")
                    st.divider()
                
                submitted = st.form_submit_button("Submit Assessment")
                if submitted:
                    for i, q in enumerate(quiz['questions']):
                        if user_answers[i] == q['correct_answer']:
                            score += 1
                    
                    total = len(quiz['questions'])
                    st.session_state.last_score = f"{score}/{total}"
                    
                    if score == total:
                        st.success(f"Amazing! Perfect score: {st.session_state.last_score}")
                        st.balloons()
                    else:
                        st.warning(f"Good effort! Score: {st.session_state.last_score}")
                        st.info("Check back with the tutor to clarify any doubts.")
            
            if st.button("Finish Review"):
                st.session_state.active_quiz = None
                st.rerun()
        else:
            st.markdown("""
            ### How it works:
            1. **Ask** the tutor to teach you a topic.
            2. **Learn** from the explanation.
            3. **Test** your knowledge! The tutor will automatically generate a quiz here once the lesson is done.
            """)
            st.image("https://img.freepik.com/free-vector/learning-concept-illustration_114360-1100.jpg", use_container_width=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Lesson Controls")
        if st.button("Reset Learning Session"):
            st.session_state.messages = []
            st.session_state.active_quiz = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.write("- Ask for 'more details' if a topic is hard.")
        st.write("- Try 'advanced' difficulty for a challenge.")

if __name__ == "__main__":
    main()
