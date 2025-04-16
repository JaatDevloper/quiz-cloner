
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import json

api_id = 28624690
api_hash = '67e6593b5a9b5ab20b11ccef6700af5b'
string_session = "BQG0xzIAc5f-B1qE4x7hijj2-zTwKUJK7T8xiUUesfTLc9I7LOs9ERluJ5GTxWiOPMzmy8UJhkBmoGakafST3sREbZ0jeM21e7-auaHHKt5a2kGCayRKBsoQcrEY2in4ZoCJlzJ5stZy7HwDkKpdjxHYEAAOBdxuR6sq6C0D1ubLqYWo6sAo-Ot_J5XGqGV3tJHCSOQ6UE10r2ASYEeVvlk2fPv3Jt-5X5gnILXAMI5DAgbanK1MilttXQoUuO7H8G9LkBSYx0x49QdLXUdNyvYJB-Cpk6rtRtqtxeN_1GceoFPHfG635fsDtedrFxL9_P4x1gMo65MEjHZallyUW5iKeFFZ9wAAAAHIW59YAA"

client = TelegramClient(StringSession(string_session), api_id, api_hash)

# This will hold the current quiz session
quiz_data = []

@client.on(events.NewMessage(pattern=r'^/clonequiz (.+)'))
async def start_clone(event):
    global quiz_data
    quiz_data = []  # reset
    quiz_title = event.pattern_match.group(1)
    await event.reply(f"Ready! Forward the @quizbot quiz polls now to collect for: **{quiz_title}**")

@client.on(events.NewMessage(func=lambda e: e.poll is not None and e.poll.quiz))
async def handle_quiz_poll(event):
    global quiz_data

    question = event.poll.question
    options = [opt.text for opt in event.poll.answers]
    correct_option_id = next((i for i, a in enumerate(event.poll.answers) if a.correct), None)

    quiz_data.append({
        "question": question,
        "options": options,
        "correct_option_id": correct_option_id
    })

    await event.reply("Question saved!")

@client.on(events.NewMessage(pattern=r'^/savequiz'))
async def save_quiz(event):
    global quiz_data
    if not quiz_data:
        await event.reply("No quiz data to save.")
        return
    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(quiz_data, f, ensure_ascii=False, indent=2)
    await event.reply("Quiz saved to questions.json!")

print("Userbot is running...")
client.start()
client.run_until_disconnected()
