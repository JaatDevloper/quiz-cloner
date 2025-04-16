
from telethon import TelegramClient, events
import json
import re
import os
import subprocess

# Your Telegram API credentials
api_id = int(os.getenv("API_ID", "28624690"))  # Replace with your actual API_ID
api_hash = os.getenv("API_HASH", "67e6593b5a9b5ab20b11ccef6700af5b")  # Replace with your actual API_HASH
session_name = os.getenv("SESSION", "BQG0xzIAc5f-B1qE4x7hijj2-zTwKUJK7T8xiUUesfTLc9I7LOs9ERluJ5GTxWiOPMzmy8UJhkBmoGakafST3sREbZ0jeM21e7-auaHHKt5a2kGCayRKBsoQcrEY2in4ZoCJlzJ5stZy7HwDkKpdjxHYEAAOBdxuR6sq6C0D1ubLqYWo6sAo-Ot_J5XGqGV3tJHCSOQ6UE10r2ASYEeVvlk2fPv3Jt-5X5gnILXAMI5DAgbanK1MilttXQoUuO7H8G9LkBSYx0x49QdLXUdNyvYJB-Cpk6rtRtqtxeN_1GceoFPHfG635fsDtedrFxL9_P4x1gMo65MEjHZallyUW5iKeFFZ9wAAAAHIW59YAA")

client = TelegramClient(session_name, api_id, api_hash)

def clean_text(text):
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(?i)created by.*|made by.*|credit.*", "", text)
    return text.strip()

def auto_git_push():
    try:
        subprocess.run(["git", "add", "questions.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Update questions"], check=True)
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("✅ Auto-pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print("❌ Git push failed:", e)

@client.on(events.NewMessage(pattern=r"/clonequiz (.+)", outgoing=True))
async def clone_quiz(event):
    if not event.is_reply:
        await event.reply("❌ Please reply to the first quiz message.")
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

    messages = list(reversed(messages))
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
    print(f"[CLONED] {len(questions)} questions saved.")

    # Push to GitHub
    auto_git_push()

client.start()
print("🚀 Userbot running. Reply to quiz and send /clonequiz <title>")
client.run_until_disconnected()
