from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key or "not-set")

SYSTEM_PROMPT = "You are a helpful assistant inside the Friends Activity Planner app."

SUMMARY_PROMPT = (
    "Summarize the conversation below into a short paragraph that preserves the important "
    "facts, decisions, and context a new conversation with this same user would need. "
    "If a previous summary is given, merge it with the new conversation into one updated summary."
)

MEMORY_PROMPT = (
    "Given this exchange between a user and an assistant, extract one short standalone fact "
    "worth remembering about the user for future conversations (preferences, plans, people, "
    "commitments, etc). Reply with just the fact in one sentence, or reply exactly NONE if "
    "nothing in this exchange is worth remembering long-term."
)


async def generate_reply(system_prompt: str, messages: list[dict]) -> str:
    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[{"role": "system", "content": system_prompt}, *messages],
    )
    return response.choices[0].message.content or ""


async def summarize_conversation(transcript: str, previous_summary: str | None) -> str:
    user_content = transcript
    if previous_summary:
        user_content = f"Previous summary:\n{previous_summary}\n\nNew conversation:\n{transcript}"

    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return response.choices[0].message.content or ""


async def extract_memory(user_message: str, assistant_reply: str) -> str | None:
    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": MEMORY_PROMPT},
            {"role": "user", "content": f"User: {user_message}\nAssistant: {assistant_reply}"},
        ],
    )
    fact = (response.choices[0].message.content or "").strip()
    return None if fact.upper() == "NONE" else fact


async def embed_text(text: str) -> list[float]:
    response = await client.embeddings.create(model=settings.openai_embedding_model, input=text)
    return response.data[0].embedding
