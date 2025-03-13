import discord
import requests
import os

# Webhook URL (あなたのWebhook URLをここに貼り付け)
WEBHOOK_URL = "https://discord.com/api/webhooks/1349340153583370362/iGi7H9jdVBI56dHW432r6_w3ZTxa1ECP_4MBWhIvTxmKqO-BcKnoZ_Me7GvC75ms-NUV"


# Botの設定
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        # DMの内容をWebhookで送信
        data = {
            "content": f"DM from {message.author.name}: {message.content}"
        }
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"DM from {message.author.name} sent successfully.")
        else:
            print(f"Failed to send DM: {response.status_code}")
bot.run(os.getenv("TOKEN"))
