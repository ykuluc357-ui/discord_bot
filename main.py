import os
import asyncio
import discord
from discord.ext import commands
from groq import AsyncGroq  # Asenkron istemci kullanımı şarttır!

# Ortam Değişkenleri
DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Async Groq İstemcisi
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# Discord Intents Ayarları
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot başarıyla bağlandı: {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="Groq AI Sohbet"))

@bot.event
async def on_message(message):
    # 1. Kendi mesajlarını ve diğer botları KESİNLİKLE yoksay (Sonsuz döngüyü önler)
    if message.author.bot:
        return

    # 2. Komut ile başlıyorsa komutu çalıştır ve AI çağrısı yapma
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # 3. Boş mesaj kontrolü
    if not message.content.strip():
        return

    # AI Yanıtı Oluşturma
    async with message.channel.typing():
        try:
            # Async Groq çağrısı (Thread'i bloklamaz)
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

            # Discord 2000 karakter sınırını aşmamak için bölme/kırpma
            if len(cevap) > 2000:
                cevaplar = [cevap[i:i+1900] for i in range(0, len(cevap), 1900)]
                for parca in cevaplar:
                    await message.channel.send(parca)
                    await asyncio.sleep(0.5)
            else:
                await message.channel.send(cevap)

        except Exception as e:
            print(f"Groq/Discord API Hatası: {e}")
            # Hata durumunda Cloudflare engeline takılmamak için kısa bir bekleme
            await asyncio.sleep(2)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ HATA: TOKEN ortam değişkeni eksik!")
    else:
        bot.run(DISCORD_TOKEN)
