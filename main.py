import os
import asyncio
import discord
from discord.ext import commands
from groq import AsyncGroq

# Environment Variables
DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Async Groq Client
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot sorunsuz bağlandı: {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="Groq AI Sohbet"))

@bot.event
async def on_message(message):
    # Kendi ve diğer botların mesajlarını yoksay
    if message.author.bot:
        return

    # Komut kontrolü
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # Boş mesaj kontrolü
    if not message.content.strip():
        return

    async with message.channel.typing():
        try:
            chat_completion = await groq_client.chat.completions.create(
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

            # 2000 Karakter Sınırı Kontrolü
            if len(cevap) > 2000:
                for i in range(0, len(cevap), 1900):
                    await message.channel.send(cevap[i:i+1900])
                    await asyncio.sleep(0.5)
            else:
                await message.channel.send(cevap)

        except Exception as e:
            print(f"Hata oluştu: {e}")

async def main():
    async with bot:
        if not DISCORD_TOKEN:
            print("❌ HATA: TOKEN bulunamadı!")
            return
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Kritik Hata: {e}")
