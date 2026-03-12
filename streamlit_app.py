import streamlit as st
import pandas as pd
from database import (init_db, create_user, get_user,
                      save_session, save_weak_topics,
                      save_study_plan, get_sessions,
                      get_weak_topics, get_stats)
from onboarding import generate_diagnostic_questions, analyze_responses
from quiz_engine import generate_question, evaluate_answer
from study_plan import generate_study_plan
from memory_manager import chat_with_coach
from progress_charts import learning_curve_chart, weak_topics_chart, score_gauge
from irt_algorithm import update_ability, ability_to_level, ability_to_score

# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Adaptive Learning Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Bricolage+Grotesque:wght@400;600;700;800&display=swap');

* { font-family: 'Bricolage Grotesque', sans-serif; }
code { font-family: 'DM Mono', monospace !important; }

.stApp { background: #F8FAFC; color: #1E293B; }

section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0;
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.metric-value {
    font-size: 28px;
    font-weight: 800;
    font-family: 'DM Mono', monospace;
}

.metric-label {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748B;
    margin-top: 4px;
}

.question-box {
    background: #FFFFFF;
    border: 1px solid #BFDBFE;
    border-radius: 12px;
    padding: 24px;
    margin: 12px 0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.correct-box {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
    color: #166534;
}

.wrong-box {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
    color: #991B1B;
}

.chat-user {
    background: #F0F9FF;
    border-left: 3px solid #60A5FA;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #1E40AF;
}

.chat-coach {
    background: #FFFFFF;
    border-left: 3px solid #10B981;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    border: 1px solid #E2E8F0;
    border-left-width: 3px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.stButton > button {
    background: #FFFFFF !important;
    color: #3B82F6 !important;
    font-weight: 600 !important;
    border: 1px solid #93C5FD !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    width: 100% !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stButton > button:hover {
    background: #EFF6FF !important;
    color: #3B82F6 !important;
    border-color: #3B82F6 !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
    transform: translateY(-1px);
}

.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    color: #1E293B !important;
    border-radius: 8px !important;
}

.stTextInput input:focus {
    border-color: #60A5FA !important;
    box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.1) !important;
}

.stTabs [data-baseweb="tab"] { color: #64748B !important; }
.stTabs [aria-selected="true"] {
    color: #3B82F6 !important;
    border-bottom-color: #3B82F6 !important;
}

h1, h2, h3, h4 { color: #0F172A !important; }
p { color: #475569; }
.stRadio label { color: #1E293B !important; }

/* Remove default dark border from selectbox and other inputs */
div[data-baseweb="select"] > div {
    background-color: white !important;
    border-color: #E2E8F0 !important;
}

/* Style for info and success boxes to match theme */
div.stAlert {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    color: #1E293B !important;
}

hr {
    border: 0;
    border-top: 1px solid #E2E8F0 !important;
    margin: 1rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Init ─────────────────────────────────────────────────────────
init_db()

# ── Session State ─────────────────────────────────────────────────
defaults = {
    "user_id": None, "user_name": "", "topic": "",
    "ability": 0.0, "onboarded": False,
    "current_question": None, "answered": False,
    "quiz_score": 0, "quiz_total": 0,
    "diag_questions": [], "diag_answers": [],
    "diag_step": 0, "chat_history": [],
    "weak_topics": []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Learning Coach")
    st.markdown("---")

    if st.session_state.user_id:
        stats = get_stats(st.session_state.user_id)
        level = ability_to_level(st.session_state.ability)
        score = ability_to_score(st.session_state.ability)

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#3B82F6">{st.session_state.user_name}</div>
            <div class="metric-label">Student</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:#10B981">{level}</div>
            <div class="metric-label">Current Level</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:#F59E0B">{score}%</div>
            <div class="metric-label">Overall Score</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:#1E293B">{stats['total_sessions']}</div>
            <div class="metric-label">Sessions Done</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"📚 **Topic:** {st.session_state.topic}")

        if st.button("🔄 Reset / New Student"):
            for k in defaults:
                st.session_state[k] = defaults[k]
            st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; padding:20px; color:#4a4a62">
            <div style="font-size:32px">🎓</div>
            <div style="font-size:13px; margin-top:8px">Login to see your progress</div>
        </div>
        """, unsafe_allow_html=True)


# ── Main Header ──────────────────────────────────────────────────
st.markdown("""
<div style="padding: 24px 0 20px">
    <div style="font-family:'DM Mono',monospace; font-size:11px; letter-spacing:.14em;
         text-transform:uppercase; color:#0EA5E9; font-weight:600; margin-bottom:10px">
        // AI-Powered Personalized Learning
    </div>
    <h1 style="font-size:36px; font-weight:800; letter-spacing:-.03em; margin:0 0 8px; color:#0F172A">
        Adaptive <span style="color:#3B82F6">Learning</span> Coach
    </h1>
    <p style="font-size:15px; color:#64748B; font-weight:400">
        AI diagnoses your weak areas → generates adaptive quizzes →
        builds personalized study plans using IRT algorithm.
    </p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# ONBOARDING — Not logged in
# ════════════════════════════════════════
if not st.session_state.user_id:
    st.markdown("### 👋 Welcome! Let's Get Started")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Your Name", placeholder="Enter your name...")
        topic = st.selectbox("What do you want to learn?", [
            "Machine Learning", "Deep Learning", "Python Programming",
            "Data Science", "Natural Language Processing",
            "Computer Vision", "Statistics"
        ])

    with col2:
        st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0;
             border-radius:12px; padding:20px; margin-top:28px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size:14px; font-weight:600; color:#1E293B; margin-bottom:12px">🚀 Learning Features</div>
            <div style="font-size:13px; color:#64748B; line-height:1.8">
                ✅ AI diagnoses your knowledge level<br>
                ✅ Adaptive quizzes using IRT algorithm<br>
                ✅ Personalized 7-day study plan<br>
                ✅ AI coach with memory<br>
                ✅ Progress tracking dashboard
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 Start Learning Journey"):
        if name.strip():
            with st.spinner("🧠 Setting up your profile..."):
                # Check existing user
                existing = get_user(name.strip())
                if existing:
                    st.session_state.user_id = existing["id"]
                    st.session_state.topic = existing["topic"]
                    st.session_state.onboarded = True
                    weak = get_weak_topics(existing["id"])
                    st.session_state.weak_topics = weak
                else:
                    uid = create_user(name.strip(), topic)
                    st.session_state.user_id = uid
                    st.session_state.topic = topic

                st.session_state.user_name = name.strip()

                if not st.session_state.onboarded:
                    questions = generate_diagnostic_questions(topic)
                    st.session_state.diag_questions = questions
                    st.session_state.diag_step = 0

            st.rerun()
        else:
            st.warning("⚠️ Please enter your name!")

# ════════════════════════════════════════
# DIAGNOSTIC — First time users
# ════════════════════════════════════════
elif not st.session_state.onboarded:
    st.markdown("### 🔍 Diagnostic Assessment")
    st.markdown("Answer these 5 questions so we can personalize your learning!")

    questions = st.session_state.diag_questions
    step = st.session_state.diag_step

    if step < len(questions):
        st.markdown(f"**Question {step+1} of {len(questions)}**")
        st.progress((step) / len(questions))

        st.markdown(f"""
        <div class="question-box">
            <p style="color:#1E293B; font-size:16px; font-weight:500">{questions[step]}</p>
        </div>
        """, unsafe_allow_html=True)

        answer = st.text_area("Your answer:", height=100, key=f"diag_{step}")

        if st.button("Next →"):
            st.session_state.diag_answers.append(answer)
            st.session_state.diag_step += 1
            st.rerun()

    else:
        with st.spinner("🧠 Analyzing your responses..."):
            analysis = analyze_responses(
                st.session_state.topic,
                questions,
                st.session_state.diag_answers
            )

            weak_topics = analysis["weak_topics"]
            save_weak_topics(st.session_state.user_id, weak_topics)
            st.session_state.weak_topics = get_weak_topics(st.session_state.user_id)

            plan = generate_study_plan(
                st.session_state.user_name,
                st.session_state.topic,
                weak_topics,
                analysis["overall_level"]
            )
            save_study_plan(st.session_state.user_id, plan)
            st.session_state.onboarded = True

        st.success("✅ Profile created! Study plan generated!")
        st.rerun()

# ════════════════════════════════════════
# MAIN APP — Logged in & onboarded
# ════════════════════════════════════════
else:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠  Adaptive Quiz",
        "📊  My Progress",
        "📅  Study Plan",
        "💬  AI Coach"
    ])

    # ── TAB 1: QUIZ ──────────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns([3, 2], gap="large")

        with col1:
            st.markdown("#### 🧠 Adaptive Quiz")
            st.markdown(f"*Topic: {st.session_state.topic} | Level: {ability_to_level(st.session_state.ability)}*")

            if st.button("🎲 Generate New Question"):
                with st.spinner("🤖 Generating question..."):
                    q = generate_question(
                        st.session_state.topic,
                        st.session_state.ability
                    )
                    st.session_state.current_question = q
                    st.session_state.answered = False

            q = st.session_state.current_question

            if q:
                st.markdown(f"""
                <div class="question-box">
                    <p style="color:#1E293B; font-size:16px; font-weight:600">
                        {q['question']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                if not st.session_state.answered:
                    answer = st.radio(
                        "Choose your answer:",
                        options=list(q["options"].keys()),
                        format_func=lambda x: f"{x}) {q['options'][x]}",
                        key="quiz_answer"
                    )

                    if st.button("✅ Submit Answer"):
                        result = evaluate_answer(q, answer)
                        correct = result["correct"]

                        # Update IRT ability
                        st.session_state.ability = update_ability(
                            st.session_state.ability,
                            correct,
                            q["difficulty"]
                        )

                        # Update score
                        st.session_state.quiz_total += 1
                        if correct:
                            st.session_state.quiz_score += 1

                        # Save session
                        score_pct = ability_to_score(st.session_state.ability)
                        save_session(
                            st.session_state.user_id,
                            st.session_state.topic,
                            score_pct,
                            q["difficulty"]
                        )

                        st.session_state.answered = True
                        st.session_state.last_result = result
                        st.rerun()

                else:
                    result = st.session_state.get("last_result", {})
                    if result.get("correct"):
                        st.markdown(f"""
                        <div class="correct-box">
                            ✅ <strong>Correct!</strong><br>
                            <span style="color:#166534; font-size:13px; opacity:0.9">
                            {result.get('explanation', '')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="wrong-box">
                            ❌ <strong>Wrong!</strong>
                            Correct answer: <strong>{result.get('correct_answer')}</strong><br>
                            <span style="color:#991B1B; font-size:13px; opacity:0.9">
                            {result.get('explanation', '')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center; padding:60px; color:#94A3B8">
                    <div style="font-size:48px">🧠</div>
                    <div style="font-size:16px; font-weight:500; margin-top:12px; color:#64748B">
                        Ready to level up?
                    </div>
                    <div style="font-size:14px; margin-top:4px">
                        Click "Generate New Question" to start your session!
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            # Score gauge
            score = ability_to_score(st.session_state.ability)
            fig = score_gauge(score)
            st.plotly_chart(fig, use_container_width=True)

            # Session stats
            total = st.session_state.quiz_total
            correct = st.session_state.quiz_score
            accuracy = round(correct/total*100) if total > 0 else 0

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#3B82F6">{total}</div>
                <div class="metric-label">Questions Answered</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#10B981">{accuracy}%</div>
                <div class="metric-label">Session Accuracy</div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 2: PROGRESS ──────────────────────────────────────────
    with tab2:
        st.markdown("#### 📊 Your Learning Progress")

        sessions = get_sessions(st.session_state.user_id)
        weak = get_weak_topics(st.session_state.user_id)

        col1, col2 = st.columns(2)
        with col1:
            fig1 = learning_curve_chart(sessions)
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = weak_topics_chart(weak)
            st.plotly_chart(fig2, use_container_width=True)

        # Sessions table
        if sessions:
            st.markdown("#### 🕐 Session History")
            df = pd.DataFrame(
                sessions,
                columns=["Topic", "Score %", "Difficulty", "Timestamp"]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── TAB 3: STUDY PLAN ────────────────────────────────────────
    with tab3:
        st.markdown("#### 📅 Your Personalized Study Plan")

        weak = get_weak_topics(st.session_state.user_id)
        level = ability_to_level(st.session_state.ability)

        if st.button("🔄 Generate New Study Plan"):
            with st.spinner("📅 Creating your personalized plan..."):
                plan = generate_study_plan(
                    st.session_state.user_name,
                    st.session_state.topic,
                    [{"topic": t[0], "score": t[1]} for t in weak],
                    level
                )
                save_study_plan(st.session_state.user_id, plan)
                st.session_state.study_plan = plan

        plan = st.session_state.get("study_plan", "")
        if plan:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0;
                 border-radius:12px; padding:24px; line-height:1.8; color:#1E293B; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                {plan.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Click 'Generate New Study Plan' to create your personalized plan!")

    # ── TAB 4: AI COACH ──────────────────────────────────────────
    with tab4:
        st.markdown("#### 💬 Chat with Your AI Coach")

        # Chat history display
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <strong>You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-coach">
                    <strong>🎓 Coach:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)

        # Input
        user_msg = st.text_input(
            "Ask your coach anything...",
            placeholder="e.g. Explain backpropagation simply",
            key="coach_input"
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("💬 Send Message"):
                if user_msg.strip():
                    # Clear input after sending
                    with st.spinner("🎓 Coach is thinking..."):
                        weak = get_weak_topics(st.session_state.user_id)
                        reply = chat_with_coach(
                            st.session_state.user_id,
                            st.session_state.user_name,
                            st.session_state.topic,
                            user_msg,
                            weak
                        )
                        st.session_state.chat_history.append(
                            {"role": "user", "content": user_msg}
                        )
                        st.session_state.chat_history.append(
                            {"role": "coach", "content": reply}
                        )
                    st.rerun()

        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
