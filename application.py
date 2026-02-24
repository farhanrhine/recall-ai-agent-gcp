import streamlit as st
from src.agent.companion import CompanionAgent
from dotenv import load_dotenv
import re
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
    st.caption("Structured learning with automated testing.")
    st.markdown("---")

    col_chat, col_study = st.columns([1.5, 1])

    with col_chat:
        st.subheader("💬 Learning Conversation")
        chat_placeholder = st.container(height=550)
        
        with chat_placeholder:
            for message in st.session_state.messages:
                role = "user" if isinstance(message, HumanMessage) else "assistant"
                with st.chat_message(role):
                    st.markdown(message.content)

        if prompt := st.chat_input("What do you want to learn today?"):
            st.session_state.messages.append(HumanMessage(content=prompt))
            with chat_placeholder:
                with st.chat_message("user"):
                    st.markdown(prompt)

            try:
                with st.spinner("Tutor is thinking..."):
                    ai_response = st.session_state.agent.chat(st.session_state.messages)
                    content = ai_response.content
                    
                    # Check for the magic [START_QUIZ: Topic] trigger
                    quiz_trigger = re.search(r"\[START_QUIZ:\s*(.*?)\]", content)
                    
                    if quiz_trigger:
                        topic = quiz_trigger.group(1).strip()
                        st.session_state.messages.append(AIMessage(content=f"I've started your quiz on **{topic}**! Check the Study Center on the right."))
                        with chat_placeholder:
                            with st.chat_message("assistant"):
                                st.markdown(f"I've started your quiz on **{topic}**! Check the Study Center on the right.")
                        
                        # Generate the actual quiz data
                        with st.spinner("Building quiz..."):
                            quiz_data = st.session_state.agent.generate_quiz_data(topic)
                            st.session_state.active_quiz = quiz_data
                            st.toast("Quiz Loaded!", icon="✅")
                            st.rerun()
                    else:
                        st.session_state.messages.append(ai_response)
                        with chat_placeholder:
                            with st.chat_message("assistant"):
                                st.markdown(content)
            except Exception as e:
                st.error(f"Tutor Error: {e}")

    with col_study:
        st.subheader("📝 Study Center")
        
        if st.session_state.active_quiz:
            quiz = st.session_state.active_quiz
            st.info(f"**Current Assessment: {quiz['topic']}**")
            
            score = 0
            user_answers = {}
            
            with st.form("sidebar_quiz_form"):
                for i, q in enumerate(quiz['questions']):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    user_answers[i] = st.radio(f"Options for Q{i+1}", q['options'], key=f"study_q_{i}")
                    st.divider()
                
                if st.form_submit_button("Submit Answers"):
                    for i, q in enumerate(quiz['questions']):
                        if user_answers[i] == q['correct_answer']:
                            score += 1
                    st.success(f"Final Score: {score}/{len(quiz['questions'])}")
                    if score == len(quiz['questions']): st.balloons()

            if st.button("Close Quiz"):
                st.session_state.active_quiz = None
                st.rerun()
        else:
            st.info("No active quiz. The tutor will send one here when you are ready!")
            st.image("https://img.freepik.com/free-vector/digital-learning-abstract-concept-vector-illustration-online-education-distance-learning-digital-school-personalized-curriculum-learning-platform-virtual-classroom-abstract-metaphor_335657-2936.jpg", use_container_width=True)

    with st.sidebar:
        if st.button("Reset Everything"):
            st.session_state.messages = []
            st.session_state.active_quiz = None
            st.rerun()

if __name__ == "__main__":
    main()
