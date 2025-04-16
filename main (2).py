
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import json
import os
import re

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
string_session = os.getenv("STRING_SESSION")
client = TelegramClient(StringSession(string_session), api_id, api_hash)

def clean_text(text):
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(?i)created by.*|made by.*|credit.*", "", text)
    return text.strip()

@client.on(events.NewMessage(pattern=r"/clonequiz (.+)", outgoing=True))
async def clone_quiz(event):
    if not event.is_reply:
        await event.reply("❌ Please reply to the first quiz poll.")
        return

    title = event.pattern_match.group(1).strip()
    start_msg = await event.get_reply_message()
    messages = []
    async for msg in client.iter_messages(event.chat_id, min_id=start_msg.id - 1, reverse=True):
        if not msg.poll or msg.poll.quiz is False:
            break
        messages.append(msg)

    if not messages:
        await event.reply("❌ No quiz polls found.")
        return

    messages.reverse()
    questions = []
    for idx, msg in enumerate(messages):
        poll = msg.poll
        question = clean_text(poll.question)
        options = [opt.text for opt in poll.answers]
        correct = poll.correct_option_id
        questions.append({
            "id": idx,
            "question": question,
            "options": options,
            "correct_option": correct
        })

    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    await event.reply(f"✅ Cloned {len(questions)} questions from quiz: {title}")

client.start()
print("✅ Userbot running with string session. Forward quiz and reply with /clonequiz <title>")
client.run_until_disconnected()
