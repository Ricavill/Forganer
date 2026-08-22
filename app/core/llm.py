import json
from collections.abc import Awaitable, Callable

from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key or "not-set")

SYSTEM_PROMPT = (
    "You are an intelligent friend-meetup organizer inside the Friends Activity Planner app. "
    "You can create, update, list, and delete activities, schedules, opinions, meets, meet "
    "groups, and friend relationships on the user's behalf using the tools available to you.\n\n"
    "When the user wants to organize a meetup around a specific activity: first find or confirm "
    "the activity, then call list_friends_interested_in_activity to see which of the user's "
    "friends have a positive opinion (like or strongly like) about it. Tell the user which "
    "friends came back interested, and explicitly ask them to confirm which of those friends "
    "(plus anyone else they want) should be invited before creating anything. Only after the "
    "user confirms the attendee list should you create the schedule, create a meet group, add "
    "the confirmed friends (and the organizer) to it, and create the meet linking them. Never "
    "invite friends or create the meet without an explicit confirmation from the user first.\n\n"
    "When you need to act on a specific person, activity, or other entity by id (e.g. sending a "
    "friend request, adding a group member), only use an id you actually obtained from a tool "
    "result - either in this turn or noted from an earlier one in this conversation. Never guess "
    "or infer an id from memory of a name alone. If you are not sure you have the right id, call "
    "the appropriate lookup tool again before acting.\n\n"
    "State such as friend requests, friendships, opinions, and memberships can change between "
    "turns - a request can be accepted, rejected, or cancelled by either side at any time, "
    'possibly outside this conversation. Never answer a question about current state ("do I have '
    'a pending request?", "have I already sent one?", "are we friends?") from memory of earlier '
    "in the conversation or from a tool result noted previously. Always call the relevant listing "
    "or lookup tool again to get the current state before answering or acting on it, even if you "
    "believe you already know the answer. The one exception is a fixed, immutable fact obtained "
    "this same turn, such as a person's id from a lookup you just made - that does not need "
    "re-verifying within the same turn.\n\n"
    "Never claim you performed an action - sent a request, created something, added a member, "
    "and so on - unless a tool call in this same turn actually returned a successful result for "
    "that exact action. If a tool call fails or returns an error, tell the user what actually "
    "happened (including the error) instead of reporting success. If you have not called the "
    "tool for an action yet, call it before describing the action as done."
)

EMAIL_INVITE_PROMPT = (
    "Email calendar invites are available in this deployment. After a meet is created, ask "
    "the user if they'd like you to email everyone a calendar invite (works with iPhone/Apple "
    "Mail, Google Calendar, Outlook, etc.) using send_meet_invites. Only call that tool after "
    "the user explicitly confirms - never send invite emails automatically."
)

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


async def generate_reply_with_tools(
    system_prompt: str,
    messages: list[dict],
    tools: list[dict],
    call_tool: Callable[[str, dict], Awaitable[str]],
) -> tuple[str, list[str]]:
    """Chat completion loop that lets the model call MCP-backed tools before
    producing its final natural-language reply.

    Returns (reply, tool_log): tool_log records each tool call made this turn
    (name, arguments, result) so the caller can persist it. Without this, the
    exact result of a tool call (e.g. a looked-up user's numeric id) is only
    ever available to the model within the turn it was called - on the next
    turn the model would have to re-derive it from its own prior prose, which
    is unreliable for things like ids.
    """
    conversation = [{"role": "system", "content": system_prompt}, *messages]
    tool_log: list[str] = []

    for _ in range(settings.bot_agent_max_tool_rounds):
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=conversation,
            tools=tools or None,
            temperature=0,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or "", tool_log

        conversation.append(message.model_dump(exclude_none=True))

        for tool_call in message.tool_calls:
            arguments = json.loads(tool_call.function.arguments or "{}")
            try:
                result = await call_tool(tool_call.function.name, arguments)
            except Exception as exc:
                result = f"Error: {exc}"

            tool_log.append(f"{tool_call.function.name}({tool_call.function.arguments}) -> {result}")
            conversation.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

    fallback = (
        "I wasn't able to finish that after several tool calls. Could you rephrase or simplify the request?"
    )
    return fallback, tool_log


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
