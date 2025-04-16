@client.on(events.NewMessage(pattern='/clonequiz (.*)'))
async def clone_quiz(event):
    custom_id = event.pattern_match.group(1).strip()  # Retrieve the custom ID
    
    try:
        # Check if message is a reply
        if not event.is_reply:
            await event.reply("⚠️ Please reply to a quiz/poll message to clone it!")
            return

        # Get the replied message
        replied_msg = await event.get_reply_message()
        if not replied_msg:
            await event.reply("❌ Could not fetch the replied message!")
            return

        # Check if it's a poll/quiz
        if not hasattr(replied_msg, 'media') or not replied_msg.media or not isinstance(replied_msg.media, MessageMediaPoll):
            await event.reply("❌ This message doesn't contain a quiz or poll!")
            return

        # Get the original poll data
        original_poll = replied_msg.media.poll
        
        # Create answers with proper string options
        answers = []
        for i, answer in enumerate(original_poll.answers):
            answers.append(PollAnswer(answer.text, str(i)))

        # Handle correct answers for quiz
        correct_answers = None
        if original_poll.quiz and hasattr(replied_msg.media, 'results') and replied_msg.media.results:
            correct_answers = []
            for i, answer in enumerate(original_poll.answers):
                if any(result.correct and result.option == answer.option 
                        for result in replied_msg.media.results.results):
                    correct_answers.append(str(i))

        # Create new poll with same settings
        new_poll = Poll(
            id=int(custom_id) if custom_id.isdigit() else 92128,  # Use custom ID or fallback to a default random id
            question=original_poll.question,
            answers=answers,
            quiz=original_poll.quiz,
            multiple_choice=original_poll.multiple_choice,
            public_voters=original_poll.public_voters,
            closed=False
        )

        # Create basic poll media
        media_poll = InputMediaPoll(
            poll=new_poll,
            correct_answers=correct_answers
        )

        # Send the cloned poll
        sent_message = await event.client.send_message(
            event.chat_id,
            file=media_poll
        )

        if sent_message:
            await event.reply("✅ Quiz/Poll cloned successfully with ID: " + custom_id)
        else:
            await event.reply("❌ Failed to send the cloned quiz/poll")

    except Exception as e:
        logger.error(f"Error in clone_quiz: {str(e)}")
        await event.reply(f"❌ Failed to clone: {str(e)}\nPlease make sure you're replying to a valid quiz/poll.")
