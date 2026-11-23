from rixstudio import RixStudio

bot = RixStudio("YOUR_BOT_TOKEN")

@bot.on_message()
async def handler(message):
    if message.text == "/start":
        await message.reply("سلام! RixStudio آماده است 🎵")
    elif message.text == "/id":
        await message.reply(f"Chat ID: {message.chat_id}")

if __name__ == "__main__":
    bot.run()
