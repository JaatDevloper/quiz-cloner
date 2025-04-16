
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import json, os, re

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
string_session = os.getenv("STRING_SESSION")

client = TelegramClient(StringSession(string_session), api_id, api_hash)

def clean(text):
    return re.sub(r"@\w+|https?://\S+|credit.*|Created by.*", "", text, flags=re.I).strip()

@client.on(events.NewMessage(pattern=r'/clonequiz (\d+)\s+(.+)'))
async def clonequiz_handler(event):
    if not event.is_reply:
        await event.reply("❌ Please reply to one of the forwarded quiz polls.")
        return

    quiz_id = event.pattern_match.group(1)
    quiz_title = event.pattern_match.group(2).strip()
    replied_msg = await event.get_reply_message()

    # Scan a batch of nearby messages (assume forwarded together)
    messages = []
    async for msg in client.iter_messages(event.chat_id, offset_id=replied_msg.id - 1, reverse=True, limit=30):
        if not msg.poll or not msg.poll.quiz:
            break
        messages.append(msg)

    if not messages:
        await event.reply("❌ No quiz polls detected around the replied message.")
        return

    messages.reverse()  # maintain original order
    questions = []

    for idx, msg in enumerate(messages):
        poll = msg.poll
        questions.append({
            "id": idx,
            "question": clean(poll.question),
            "options": [o.text for o in poll.answers],
            "correct_option": poll.correct_option_id
        })

    os.makedirs("quizzes", exist_ok=True)
    filepath = f"quizzes/{quiz_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    await event.reply(f"✅ Cloned {len(questions)} questions as `{filepath}`")

print("✅ Userbot is running. Reply to quiz & use /clonequiz <id> <title>")
client.start()
client.run_until_disconnected()
