# xLink Relay Bot (자동 채널 생성 + 서버 내 중계 설정)
# Copyright (c) Juno / JUNOSPACE

import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

relay_channels = {}  # {guild_id: {"text": text_channel_id, "voice": voice_channel_id}}

@bot.event
async def on_ready():
    print(f"✅ xLink 봇 작동 시작: {bot.user}")

@bot.event
async def on_guild_join(guild):
    # 텍스트 채널 생성
    text_channel = await guild.create_text_channel("xlink-중계")
    voice_channel = await guild.create_voice_channel("xlink-보이스")

    relay_channels[guild.id] = {
        "text": text_channel.id,
        "voice": voice_channel.id
    }

    await text_channel.send("✅ xLink 중계 채널이 생성되었습니다. 이 채널에 작성한 메시지는 상대 서버로 중계됩니다.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id
    if guild_id not in relay_channels:
        return

    config = relay_channels[guild_id]
    if message.channel.id != config["text"]:
        return

    relay_msg = f"📡 `{message.author.display_name}`:\n{message.content}"

    # 음성 채널 링크 추가
    vc_channel = None
    for vc in message.guild.voice_channels:
        if message.author in vc.members:
            vc_channel = vc
            break

    if vc_channel:
        try:
            vc_url = f"https://discord.com/channels/{message.guild.id}/{vc_channel.id}"
            invite = await vc_channel.create_invite(max_age=3600, max_uses=5, unique=True)
            invite_url = invite.url
            relay_msg += f"\n🔊 **음성 참여 링크**: [서버 입장]({invite_url}) | [바로 입장]({vc_url})"
        except discord.Forbidden:
            relay_msg += "\n⚠️ 음성 초대링크를 생성할 권한이 없습니다."

    # 중계 대상 찾기: 나 외의 다른 서버
    for other_id, other_config in relay_channels.items():
        if other_id != guild_id:
            target_channel = bot.get_channel(other_config["text"])
            if target_channel:
                await target_channel.send(relay_msg)

    await bot.process_commands(message)

bot.run(TOKEN)
