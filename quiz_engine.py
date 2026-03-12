import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from irt_algorithm import get_next_difficulty, ability_to_level

load_dotenv()

ALL_MODELS = [
    {"provider": "groq",   "model": "gemma2-9b-it"},
    {"provider": "groq",   "model": "llama-3.1-8b-instant"},
    {"provider": "groq",   "model": "mixtral-8x7b-32738"},
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
                    temperature=0.5
                )
            else:
                llm = ChatGoogleGenerativeAI(
                    model=entry["model"],
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                    temperature=0.5
                )
            llm.invoke("OK")
            return llm
        except Exception as e:
            if "429" in str(e) or "quota" in str(e):
                continue
    return None


def generate_question(topic: str, ability: float) -> dict:
    """Generate adaptive question based on current ability"""
    llm = get_llm()
    if not llm:
        return None

    difficulty = get_next_difficulty(ability)
    level = ability_to_level(ability)

    # Map difficulty to words
    if difficulty > 1.0:
        diff_word = "very hard (expert level)"
    elif difficulty > 0.0:
        diff_word = "medium-hard (intermediate-advanced)"
    elif difficulty > -1.0:
        diff_word = "medium (beginner-intermediate)"
    else:
        diff_word = "easy (beginner level)"

    system = SystemMessage(content=f"""You are an expert quiz generator.
Generate ONE multiple choice question about {topic}.
Difficulty: {diff_word}
Student Level: {level}

Return in EXACT format:
QUESTION: your question here
A) option a
B) option b
C) option c
D) option d
ANSWER: A or B or C or D
EXPLANATION: brief explanation of correct answer""")

    user = HumanMessage(content=f"Generate one {diff_word} question about {topic}.")

    try:
        response = llm.invoke([system, user])
        return parse_question(response.content, difficulty)
    except:
        return None


def parse_question(text: str, difficulty: float) -> dict:
    """Parse LLM response into structured question"""
    lines = text.strip().split("\n")
    question = ""
    options = {}
    answer = ""
    explanation = ""

    for line in lines:
        line = line.strip()
        if line.startswith("QUESTION:"):
            question = line.replace("QUESTION:", "").strip()
        elif line.startswith("A)"):
            options["A"] = line.replace("A)", "").strip()
        elif line.startswith("B)"):
            options["B"] = line.replace("B)", "").strip()
        elif line.startswith("C)"):
            options["C"] = line.replace("C)", "").strip()
        elif line.startswith("D)"):
            options["D"] = line.replace("D)", "").strip()
        elif line.startswith("ANSWER:"):
            answer = line.replace("ANSWER:", "").strip()
        elif line.startswith("EXPLANATION:"):
            explanation = line.replace("EXPLANATION:", "").strip()

    return {
        "question":    question,
        "options":     options,
        "answer":      answer,
        "explanation": explanation,
        "difficulty":  difficulty
    }


def evaluate_answer(question: dict, user_answer: str) -> dict:
    """Check if answer is correct"""
    correct = user_answer.upper() == question["answer"].upper()
    return {
        "correct":     correct,
        "user_answer": user_answer,
        "correct_answer": question["answer"],
        "explanation": question["explanation"]
    }


if __name__ == "__main__":
    print("🧪 Testing quiz engine...")
    q = generate_question("Machine Learning", 0.0)
    if q:
        print(f"Question: {q['question']}")
        for k, v in q['options'].items():
            print(f"  {k}) {v}")
        print(f"Answer: {q['answer']}")
        print(f"Difficulty: {q['difficulty']}")
