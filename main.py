import os
import discord
from discord.ext import commands
from groq import Groq

# Render panelindeki KEY isimleriyle birebir aynı (TOKEN ve GROQ_API_KEY)
DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq İstemcisi
groq_client = Groq(api_key=GROQ_API_KEY)

# Discord Yetkileri
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot Render üzerinde aktif! {bot.user.name} online.")
    await bot.change_presence(activity=discord.Game(name="Groq AI Sohbet"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    async with message.channel.typing():
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sen Discord sunucusunda takılan samimi, eğlenceli ve yardımsever bir botursun. "
                            "Yanıtlarını Discord formatına uygun, kısa ve doğal bir Türkçe ile ver."
                        )
                    },
                    {"role": "user", "content": message.content}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=500
            )

            cevap = chat_completion.choices[0].message.content
            
            if len(cevap) > 2000:
                cevap = cevap[:1995] + "..."

            await message.channel.send(cevap)

        except Exception as e:
            print(f"Hata: {e}")
            await message.channel.send("Ufak bir bağlantı sorunu yaşadım, tekrar dener misin?")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
