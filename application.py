import streamlit as st
from src.agent.companion import CompanionAgent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

def main():
    st.set_page_config(page_title="Intelligent AI Tutor", page_icon="🎓", layout="wide")

    # Custom CSS for premium feel
    st.markdown("""
        <style>
        .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
        .stButton button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
        .quiz-card { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border-left: 5px solid #4CAF50; }
        </style>
    """, unsafe_allow_html=True)

    if "agent" not in st.session_state:
        st.session_state.agent = CompanionAgent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "active_quiz" not in st.session_state:
        st.session_state.active_quiz = None

    if "quiz_button_visible" not in st.session_state:
        st.session_state.quiz_button_visible = False

    st.title("🎓 Intelligent AI Tutor")
    st.caption("Expert-led technical training with contextual assessments.")
    st.markdown("---")

    col_chat, col_study = st.columns([1.5, 1])

    with col_chat:
        st.subheader("💬 Learning Path")
        chat_placeholder = st.container(height=550)
        
        with chat_placeholder:
            for message in st.session_state.messages:
                role = "user" if isinstance(message, HumanMessage) else "assistant"
                with st.chat_message(role):
                    st.markdown(message.content)

        # Chat Input logic
        if prompt := st.chat_input("Ask a question or start a topic..."):
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.session_state.quiz_button_visible = False # Hide button on new user input
            with chat_placeholder:
                with st.chat_message("user"):
                    st.markdown(prompt)

            try:
                with st.spinner("Tutor is thinking..."):
                    ai_response = st.session_state.agent.chat(st.session_state.messages)
                    st.session_state.messages.append(ai_response)
                    
                    # Log AI response
                    with chat_placeholder:
                        with st.chat_message("assistant"):
                            st.markdown(ai_response.content)
                    
                    # Check if AI suggested a quiz
                    if "Use the button below to start!" in ai_response.content:
                        st.session_state.quiz_button_visible = True
                    
                    st.rerun()
            except Exception as e:
                st.error(f"Tutor Error: {e}")

        # Persistent 'Take Quiz' Button at the bottom of chat if triggered
        if st.session_state.quiz_button_visible:
            st.markdown("---")
            if st.button("🚀 Start Contextual Quiz Now", type="primary"):
                with st.spinner("Analyzing lesson context and building quiz..."):
                    quiz_data = st.session_state.agent.generate_quiz_from_history(st.session_state.messages)
                    if quiz_data.get("type") == "quiz_data":
                        st.session_state.active_quiz = quiz_data
                        st.session_state.quiz_button_visible = False
                        st.toast("Quiz Generated from Lesson Context!", icon="🧠")
                        st.rerun()
                    else:
                        st.error(f"Quiz Generation Error: {quiz_data.get('message')}")

    with col_study:
        st.subheader("📝 Assessment Center")
        
        if st.session_state.active_quiz:
            quiz = st.session_state.active_quiz
            st.markdown(f'<div class="quiz-card">Checking your knowledge on the recent discussion.</div>', unsafe_allow_html=True)
            st.write("")
            
            score = 0
            user_answers = {}
            
            with st.form("current_lesson_quiz"):
                for i, q in enumerate(quiz['questions']):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    # Set index=None so no option is pre-selected
                    user_answers[i] = st.radio(f"Options for Q{i+1}", q['options'], key=f"study_q_{i}", index=None)
                    
                    if st.session_state.get("quiz_submitted"):
                        # Use case-insensitive stripped comparison, handling None
                        user_ans = (user_answers[i] or "").strip().lower()
                        correct_ans = q['correct_answer'].strip().lower()
                        if user_ans == correct_ans:
                            st.success(f"Correct!")
                        else:
                            st.error(f"Incorrect. Correct answer: {q['correct_answer']}")
                    st.divider()
                
                # Submit button must ALWAYS be rendered within the form
                submitted = st.form_submit_button("Submit Assessment", disabled=st.session_state.get("quiz_submitted", False))
                if submitted:
                    # Optional: check if all answered
                    if any(a is None for a in user_answers.values()):
                        st.warning("Please answer all questions before submitting.")
                    else:
                        st.session_state.quiz_submitted = True
                        correct_count = 0
                        for i, q in enumerate(quiz['questions']):
                            user_ans = (user_answers[i] or "").strip().lower()
                            if user_ans == q['correct_answer'].strip().lower():
                                correct_count += 1
                        
                        st.session_state.last_score_val = correct_count
                        st.session_state.last_total_val = len(quiz['questions'])
                        st.rerun()

            if st.session_state.get("quiz_submitted"):
                score = st.session_state.last_score_val
                total = st.session_state.last_total_val
                if score == total:
                    st.success(f"Perfect! {score}/{total}")
                    st.balloons()
                else:
                    st.warning(f"Result: {score}/{total}. Talk to the tutor to clear doubts!")
                
                if st.button("Close Quiz"):
                    st.session_state.active_quiz = None
                    st.session_state.quiz_submitted = False
                    st.rerun()
        else:
            st.info("Your assessments based on what the tutor teaches will appear here.")
            st.image("https://img.freepik.com/free-vector/knowledge-concept-illustration_114360-2646.jpg", width='stretch')

    with st.sidebar:
        st.header("Admin")
        if st.button("New Session"):
            st.session_state.messages = []
            st.session_state.active_quiz = None
            st.session_state.quiz_button_visible = False
            st.rerun()

if __name__ == "__main__":
    main()
