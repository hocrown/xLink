# xLink Relay Bot (통합 채널 구조 + 음성 채널 링크 + 초대 링크 fallback)
# Copyright (c) Juno / JUNOSPACE

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))  # 현재 서버의 송신 채널
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))  # 상대 서버의 수신 채널

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ xLink 봇 작동 시작: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # 봇 메시지 무시

    if message.channel.id != SOURCE_CHANNEL_ID:
        return  # 송신 채널이 아니면 무시

    relay_msg = f"📡 `{message.author.display_name}`:\n{message.content}"

    # 음성 채널 확인
    vc_channel = None
    for vc in message.guild.voice_channels:
        if message.author in vc.members:
            vc_channel = vc
            break

    # 음성 채널 링크 추가
    if vc_channel:
        try:
            # 음성 채널 직접 링크
            vc_url = f"https://discord.com/channels/{message.guild.id}/{vc_channel.id}"
            # 초대 링크 fallback
            invite = await vc_channel.create_invite(max_age=3600, max_uses=5, unique=True)
            invite_url = invite.url
            relay_msg += f"\n🔊 **음성 참여 링크**: [서버 입장]({invite_url}) | [바로 입장]({vc_url})"
        except discord.Forbidden:
            relay_msg += "\n⚠️ 음성 초대링크를 생성할 권한이 없습니다."

    # 대상 채널로 전송
    target_channel = bot.get_channel(TARGET_CHANNEL_ID)
    if target_channel:
        await target_channel.send(relay_msg)

    await bot.process_commands(message)

bot.run(TOKEN)
