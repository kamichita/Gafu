import discord
import requests
import re
import time

# Webhook URL (あなたのWebhook URLをここに貼り付け)
WEBHOOK_URL = "https://discord.com/api/webhooks/1349340153583370362/iGi7H9jdVBI56dHW432r6_w3ZTxa1ECP_4MBWhIvTxmKqO-BcKnoZ_Me7GvC75ms-NUV"

# Discord Botトークン


# リンク判定の正規表現パターン
URL_PATTERN = r"(https?://[^\s]+)"

# ユーザーのリンク送信履歴とブラックリスト
user_link_history = {}
blacklist = set()

# 管理者IDリスト（デフォルトで1つの管理者IDを設定）

admin_ids = [1198256209833238572, 1109692644348661852]


# Botの設定
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 管理者追加コマンド
    if message.content.startswith("!addadmin"):
        try:
            new_admin_id = int(message.content.split(" ")[1])
            if message.author.id in admin_ids:
                admin_ids.add(new_admin_id)
                await message.channel.send(f"✅ 管理者ID {new_admin_id} を追加しました。")
                print(f"✅ Admin ID {new_admin_id} added.")
            else:
                await message.channel.send("❌ あなたには管理者権限がありません。")
        except (IndexError, ValueError):
            await message.channel.send("❌ コマンドの形式が正しくありません。使用方法: `!addadmin <ユーザーID>`")
        return

    # 管理者削除コマンド
    if message.content.startswith("!removeadmin"):
        try:
            remove_admin_id = int(message.content.split(" ")[1])
            if message.author.id in admin_ids:
                if remove_admin_id in admin_ids:
                    admin_ids.remove(remove_admin_id)
                    await message.channel.send(f"✅ 管理者ID {remove_admin_id} を削除しました。")
                    print(f"✅ Admin ID {remove_admin_id} removed.")
                else:
                    await message.channel.send("❌ 指定されたIDは管理者ではありません。")
            else:
                await message.channel.send("❌ あなたには管理者権限がありません。")
        except (IndexError, ValueError):
            await message.channel.send("❌ コマンドの形式が正しくありません。使用方法: `!removeadmin <ユーザーID>`")
        return

    # 管理者リスト表示コマンド
    if message.content.startswith("!listadmins"):
        if message.author.id in admin_ids:
            admin_list = ", ".join(str(admin_id) for admin_id in admin_ids)
            await message.channel.send(f"📝 現在の管理者IDリスト: {admin_list}")
        else:
            await message.channel.send("❌ あなたには管理者権限がありません。")
        return

    # DMの内容をWebhookで送信
    if isinstance(message.channel, discord.DMChannel):
        data = {
            "content": f"DM from {message.author.name}: {message.content}"
        }
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"DM from {message.author.name} sent successfully.")
        else:
            print(f"Failed to send DM: {response.status_code}")

    # リンクが含まれているかチェック
    if re.search(URL_PATTERN, message.content):
        current_time = time.time()
        user_id = message.author.id

        # ブラックリストに登録されているか確認
        if user_id in blacklist:
            for admin_id in admin_ids:
                admin = await bot.fetch_user(admin_id)
                await admin.send(f"🚨 警告: ブラックリストに登録されているユーザー {message.author.name} が再度リンクを送信しました。")
            return

        # ユーザーのリンク送信履歴を更新
        if user_id not in user_link_history:
            user_link_history[user_id] = []
        user_link_history[user_id].append(current_time)

        # 4秒以内に4回以上リンク送信でブラックリストに登録
        recent_links = [t for t in user_link_history[user_id] if current_time - t <= 4]
        if len(recent_links) >= 4:
            blacklist.add(user_id)
            for admin_id in admin_ids:
                admin = await bot.fetch_user(admin_id)
                await admin.send(f"🚫 ユーザー {message.author.name} が4秒以内に複数回リンクを送信しました。ブラックリストに登録しました。")
            print(f"🚫 User {message.author.name} added to blacklist.")
            return

bot.run(os.getenv("TOKEN"))
