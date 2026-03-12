import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

ALL_MODELS = [
    {"provider": "groq",   "model": "gemma2-9b-it"},
    {"provider": "groq",   "model": "llama-3.1-8b-instant"},
    {"provider": "gemini", "model": "gemini-2.0-flash"},
    {"provider": "gemini", "model": "gemini-1.5-flash"},
]


def get_llm():
    for entry in ALL_MODELS:
        try:
            if entry["provider"] == "groq":
                llm = ChatGroq(
                    model=entry["model"],
                    groq_api_key=os.getenv("GROQ_API_KEY"),
                    temperature=0.4
                )
            else:
                llm = ChatGoogleGenerativeAI(
                    model=entry["model"],
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                    temperature=0.4
                )
            llm.invoke("OK")
            return llm
        except Exception as e:
            if "429" in str(e) or "quota" in str(e):
                continue
    return None


def generate_study_plan(name: str, topic: str,
                        weak_topics: list, level: str) -> str:
    """Generate personalized 7-day study plan"""
    llm = get_llm()
    if not llm:
        return "Study plan unavailable — API rate limited."

    weak_str = ", ".join([t["topic"] for t in weak_topics]) if weak_topics else "General concepts"

    system = SystemMessage(content="""You are an expert learning coach.
Create a personalized 7-day study plan.
Be specific, actionable and encouraging.
Format as:
DAY 1: [Topic] — [What to study] — [Resource type]
DAY 2: ...
...
DAY 7: ...
WEEKLY GOAL: one sentence goal""")

    user = HumanMessage(content=f"""
Student: {name}
Main Topic: {topic}
Current Level: {level}
Weak Areas: {weak_str}

Create a personalized 7-day study plan to improve weak areas.""")

    response = llm.invoke([system, user])
    return response.content


def generate_weekly_report(name: str, topic: str,
                           sessions: list, improvement: float) -> str:
    """Generate weekly progress report"""
    llm = get_llm()
    if not llm:
        return "Report unavailable."

    session_summary = f"{len(sessions)} sessions completed, {improvement:.1f}% improvement"

    system = SystemMessage(content="""You are an encouraging learning coach.
Write a brief weekly progress report (3-4 sentences).
Be specific, motivating and actionable.""")

    user = HumanMessage(content=f"""
Student: {name}
Topic: {topic}
Progress: {session_summary}
Write an encouraging weekly report.""")

    response = llm.invoke([system, user])
    return response.content


if __name__ == "__main__":
    print("🧪 Testing study plan...")
    weak = [{"topic": "Backpropagation", "score": 30},
            {"topic": "Regularization", "score": 40}]
    plan = generate_study_plan("Madhu", "Machine Learning", weak, "Beginner")
    print(plan)
