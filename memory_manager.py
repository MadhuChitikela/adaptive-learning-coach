import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
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


# In-memory conversation store per user
_conversations = {}


def get_memory(user_id: int) -> ConversationBufferWindowMemory:
    """Get or create memory for a user"""
    if user_id not in _conversations:
        _conversations[user_id] = ConversationBufferWindowMemory(
            k=10,
            return_messages=True
        )
    return _conversations[user_id]


def chat_with_coach(user_id: int, name: str,
                    topic: str, message: str,
                    weak_topics: list = None) -> str:
    """
    Personal AI coach with memory.
    Remembers conversation history per user.
    """
    llm = get_llm()
    if not llm:
        return "Coach unavailable — API rate limited. Try again shortly!"

    memory = get_memory(user_id)
    history = memory.load_memory_variables({})
    messages_history = history.get("history", [])

    weak_str = ""
    if weak_topics:
        weak_str = f"Student's weak areas: {', '.join([t[0] for t in weak_topics[:3]])}"

    system = SystemMessage(content=f"""You are an expert, encouraging learning coach.
Student name: {name}
Topic they are studying: {topic}
{weak_str}

Your role:
- Answer questions clearly and simply
- Give examples when explaining concepts
- Be encouraging and motivating
- Reference their weak areas when relevant
- Keep responses concise (3-5 sentences max)
- Use emojis occasionally to keep it friendly""")

    all_messages = [system] + messages_history + [HumanMessage(content=message)]

    response = llm.invoke(all_messages)
    reply = response.content

    # Save to memory
    memory.save_context(
        {"input": message},
        {"output": reply}
    )

    return reply


def clear_memory(user_id: int):
    """Clear conversation history for user"""
    if user_id in _conversations:
        del _conversations[user_id]


if __name__ == "__main__":
    print("🧪 Testing memory manager...")
    reply1 = chat_with_coach(1, "Madhu", "Machine Learning",
                              "What is gradient descent?")
    print(f"Coach: {reply1[:100]}...")

    reply2 = chat_with_coach(1, "Madhu", "Machine Learning",
                              "Can you give me an example?")
    print(f"Coach (with memory): {reply2[:100]}...")
