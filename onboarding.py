import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

ALL_MODELS = [
    {"provider": "groq",   "model": "gemma2-9b-it"},
    {"provider": "groq",   "model": "llama-3.1-8b-instant"},
    {"provider": "groq",   "model": "mixtral-8x7b-32768"},
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
                    temperature=0.3
                )
            else:
                llm = ChatGoogleGenerativeAI(
                    model=entry["model"],
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                    temperature=0.3
                )
            llm.invoke("OK")
            print(f"✅ Using [{entry['provider']}] {entry['model']}")
            return llm
        except Exception as e:
            if "429" in str(e) or "quota" in str(e):
                continue
    return None


def generate_diagnostic_questions(topic: str) -> list:
    """Generate 5 diagnostic questions to assess student level"""
    llm = get_llm()
    if not llm:
        return []

    system = SystemMessage(content="""You are an expert educator.
Generate exactly 5 diagnostic questions to assess a student's knowledge.
Questions should range from basic to advanced.
Return ONLY a numbered list:
1. question one
2. question two
3. question three
4. question four
5. question five""")

    user = HumanMessage(content=f"Generate 5 diagnostic questions for topic: {topic}")

    response = llm.invoke([system, user])
    lines = response.content.strip().split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            q = line.lstrip("0123456789.) ").strip()
            if q:
                questions.append(q)
    return questions[:5]


def analyze_responses(topic: str, questions: list, answers: list) -> dict:
    """Analyze student responses to find weak areas"""
    llm = get_llm()
    if not llm:
        return {"weak_topics": [], "strong_topics": [], "overall_level": "Beginner"}

    qa_text = "\n".join([
        f"Q: {q}\nA: {a}"
        for q, a in zip(questions, answers)
    ])

    system = SystemMessage(content="""You are an expert educator analyzing student responses.
Identify weak and strong areas.
Respond in this EXACT format:
WEAK: topic1, topic2, topic3
STRONG: topic1, topic2
LEVEL: Beginner OR Intermediate OR Advanced""")

    user = HumanMessage(content=f"""
Topic: {topic}
Student Q&A:
{qa_text}

Analyze and identify weak areas.""")

    response = llm.invoke([system, user])
    lines = response.content.strip().split("\n")

    weak = []
    strong = []
    level = "Beginner"

    for line in lines:
        if line.startswith("WEAK:"):
            items = line.replace("WEAK:", "").strip().split(",")
            weak = [{"topic": t.strip(), "score": 30.0} for t in items if t.strip()]
        elif line.startswith("STRONG:"):
            items = line.replace("STRONG:", "").strip().split(",")
            strong = [t.strip() for t in items if t.strip()]
        elif line.startswith("LEVEL:"):
            level = line.replace("LEVEL:", "").strip()

    return {
        "weak_topics":   weak,
        "strong_topics": strong,
        "overall_level": level
    }


if __name__ == "__main__":
    print("🧪 Testing onboarding...")
    questions = generate_diagnostic_questions("Machine Learning")
    print("Questions generated:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
