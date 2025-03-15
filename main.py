import discord
import requests
import re
import time
import os
import json

# Webhook URL (あなたのWebhook URLをここに貼り付け)
WEBHOOK_URL = "https://discord.com/api/webhooks/1349340153583370362/iGi7H9jdVBI56dHW432r6_w3ZTxa1ECP_4MBWhIvTxmKqO-BcKnoZ_Me7GvC75ms-NUV"

# リンク判定の正規表現パターン
URL_PATTERN = r"(https?://[^\s]+)"

# データファイルのパス
BLACKLIST_FILE = "blacklist.json"
ADMINS_FILE = "admins.json"

# ブラックリストの読み込み
if os.path.exists(BLACKLIST_FILE):
    with open(BLACKLIST_FILE, "r") as f:
        blacklist = set(json.load(f))
else:
    blacklist = set()

# 管理者の読み込み
if os.path.exists(ADMINS_FILE):
    with open(ADMINS_FILE, "r") as f:
        admin_ids = set(json.load(f))
else:
    admin_ids = set()

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True
bot = discord.Client(intents=intents)

# ユーザーのリンク送信履歴
user_link_history = {}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # !help-command コマンド - コマンド一覧
    if message.content == "!help-command":
        help_text = (
            "📝 **利用可能なコマンド**:\n"
            "1. `!help-command` - コマンド一覧を表示\n"
            "2. `!addadmin <ユーザーID>` - 管理者を追加\n"
            "3. `!removeadmin <ユーザーID>` - 管理者を削除\n"
            "4. `!listadmins` - 管理者リストを表示\n"
            "5. `!black <ユーザーID>` - ユーザーをブラックリストに追加\n"
            "6. `!unblacklist <ユーザーID>` - ブラックリスト解除\n"
            "7. `!list-black` - ブラックリストの表示"
        )
        await message.channel.send(help_text)
        return

    # 管理者追加コマンド
    if message.content.startswith("!addadmin"):
        try:
            new_admin_id = int(message.content.split(" ")[1])
            if message.author.id in admin_ids:
                admin_ids.add(new_admin_id)
                with open(ADMINS_FILE, "w") as f:
                    json.dump(list(admin_ids), f)
                await message.channel.send(f"✅ 管理者ID {new_admin_id} を追加しました。")
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
                    with open(ADMINS_FILE, "w") as f:
                        json.dump(list(admin_ids), f)
                    await message.channel.send(f"✅ 管理者ID {remove_admin_id} を削除しました。")
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

    # !helpmeeコマンドで自分を管理者に追加
    if message.content == "!helpmee":
        if message.author.id not in admin_ids:
            admin_ids.add(message.author.id)
            with open(ADMINS_FILE, "w") as f:
                json.dump(list(admin_ids), f)
            await message.channel.send(f"✅ {message.author.name} さんを管理者として追加しました。")
        else:
            await message.channel.send("❌ あなたはすでに管理者です。")
        return

    # ブラックリストに追加するコマンド
    if message.content.startswith("!black"):
        if message.author.id in admin_ids:
            try:
                user_id_to_blacklist = int(message.content.split(" ")[1])
                blacklist.add(user_id_to_blacklist)
                with open(BLACKLIST_FILE, "w") as f:
                    json.dump(list(blacklist), f)
                await message.channel.send(f"✅ ユーザー {user_id_to_blacklist} をブラックリストに追加しました。")
            except (IndexError, ValueError):
                await message.channel.send("❌ コマンドの形式が正しくありません。使用方法: `!black <ユーザーID>`")
        else:
            await message.channel.send("❌ あなたには管理者権限がありません。")
        return

    # ブラックリスト表示コマンド
    if message.content == "!list-black":
        if message.author.id in admin_ids:
            blacklist_list = ", ".join(str(user_id) for user_id in blacklist)
            await message.channel.send(f"📝 現在のブラックリスト: {blacklist_list}")
        else:
            await message.channel.send("❌ あなたには管理者権限がありません。")
        return

    # ブラックリスト解除コマンド
    if message.content.startswith("!unblacklist"):
        if message.author.id in admin_ids:
            try:
                user_id_to_remove = int(message.content.split(" ")[1])
                if user_id_to_remove in blacklist:
                    blacklist.remove(user_id_to_remove)
                    with open(BLACKLIST_FILE, "w") as f:
                        json.dump(list(blacklist), f)
                    await message.channel.send(f"✅ ユーザー {user_id_to_remove} のブラックリストを解除しました。")
                else:
                    await message.channel.send("❌ 指定されたユーザーはブラックリストにありません。")
            except (IndexError, ValueError):
                await message.channel.send("❌ コマンドの形式が正しくありません。使用方法: `!unblacklist <ユーザーID>`")
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
            with open(BLACKLIST_FILE, "w") as f:
                json.dump(list(blacklist), f)
            for admin_id in admin_ids:
                admin = await bot.fetch_user(admin_id)
                await admin.send(f"🚫 ユーザー {message.author.name} が4秒以内に複数回リンクを送信しました。ブラックリストに登録しました。")
            print(f"🚫 User {message.author.name} added to blacklist.")
            return

bot.run(os.getenv("TOKEN"))
