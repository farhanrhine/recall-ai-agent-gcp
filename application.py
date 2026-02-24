import streamlit as st
from src.agent.companion import CompanionAgent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

def main():
    st.set_page_config(page_title="Personal AI Agent Master", page_icon="🧬", layout="wide")

    if "agent" not in st.session_state:
        st.session_state.agent = CompanionAgent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None

    st.title("🧬 Personal AI Agent Master")
    st.markdown("---")

    # Create Tabs for different modes
    tab1, tab2 = st.tabs(["💬 Chat Assistant", "📝 Quiz Master"])

    with tab1:
        st.subheader("General Agentic Support")
        chat_container = st.container(height=500)
        
        with chat_container:
            for message in st.session_state.messages:
                role = "user" if isinstance(message, HumanMessage) else "assistant"
                with st.chat_message(role):
                    st.markdown(message.content)

        if prompt := st.chat_input("Talk to your agent...", key="chat_input"):
            st.session_state.messages.append(HumanMessage(content=prompt))
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            try:
                with st.spinner("Processing..."):
                    new_messages = st.session_state.agent.chat(st.session_state.messages)
                    for msg in new_messages:
                        if isinstance(msg, AIMessage) and msg.content:
                            st.session_state.messages.append(msg)
                            with chat_container:
                                with st.chat_message("assistant"):
                                    st.markdown(msg.content)
            except Exception as e:
                st.error(f"Chat Error: {e}")

    with tab2:
        st.subheader("Structured Study System")
        
        col_settings, col_display = st.columns([1, 2])
        
        with col_settings:
            st.info("Configure your quiz here")
            topic = st.text_input("Topic", placeholder="e.g. Kubernetes, Photosynthesis, Python")
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
            num_questions = st.slider("Number of Questions", 1, 10, 5)
            
            if st.button("Generate Quiz 🚀", use_container_width=True):
                if not topic:
                    st.warning("Please enter a topic first!")
                else:
                    try:
                        with st.spinner("Generating specialized questions..."):
                            questions = st.session_state.agent.generate_quiz(topic, num_questions, difficulty)
                            st.session_state.quiz_data = questions
                            st.session_state.quiz_submitted = False
                            st.rerun()
                    except Exception as e:
                        st.error(f"Generation Error: {e}")

        with col_display:
            if st.session_state.quiz_data:
                st.success(f"Generated {len(st.session_state.quiz_data)} questions on **{topic if topic else 'requested topic'}**")
                
                score = 0
                user_answers = {}
                
                with st.form("structured_quiz"):
                    for i, q in enumerate(st.session_state.quiz_data):
                        st.write(f"**Question {i+1}:** {q.question}")
                        user_answers[i] = st.radio(f"Select an option for Q{i+1}", q.options, key=f"quiz_q_{i}")
                        st.divider()
                    
                    submitted = st.form_submit_button("Submit Quiz ✅")
                    if submitted:
                        st.session_state.quiz_submitted = True
                        for i, q in enumerate(st.session_state.quiz_data):
                            if user_answers[i] == q.correct_answer:
                                score += 1
                        
                        st.session_state.last_score = score
                
                if st.session_state.get("quiz_submitted"):
                    total = len(st.session_state.quiz_data)
                    percentage = (st.session_state.last_score / total) * 100
                    
                    st.metric("Final Score", f"{st.session_state.last_score} / {total}", f"{percentage}%")
                    
                    if percentage == 100:
                        st.balloons()
                        st.success("Perfect Score! You're a master.")
                    elif percentage >= 70:
                        st.success("Great job! You have a solid understanding.")
                    else:
                        st.warning("Keep studying! You'll get there.")
                    
                    if st.button("Clear Quiz"):
                        st.session_state.quiz_data = None
                        st.rerun()
            else:
                st.info("Your generated quiz will appear here. Set the topic in the left pane and click Generate.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Controls")
        if st.button("Reset Session Memory"):
            st.session_state.messages = []
            st.session_state.quiz_data = None
            st.rerun()
        st.markdown("---")
        st.write("Using Latest LangChain Agents & Groq (Llama 3.1)")

if __name__ == "__main__":
    main()
