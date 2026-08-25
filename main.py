import os
import asyncio
import discord
from discord.ext import commands
from groq import AsyncGroq

# Environment Variables
DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq istemcisini başlangıçta None olarak bırakıyoruz (çökmeyi önler)
groq_client = None

def get_groq_client():
    global groq_client
    if groq_client is None:
        # İstemci ilk kez ihtiyaç duyulduğunda güvenle oluşturulur
        groq_client = AsyncGroq(api_key=GROQ_API_KEY)
    return groq_client

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot başarıyla çalıştı ve bağlandı: {bot.user.name}")
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
            # Groq istemcisini çağır
            client = get_groq_client()
            
            chat_completion = await client.chat.completions.create(
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
            print(f"Groq API Hatası: {e}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
    else:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"Kritik Bot Çalıştırma Hatası: {e}")
