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
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

relay_channels = {}  # {guild_id: {"text": id, "target": id}}





@tree.command(name="help", description="📖 xLink 봇 명령어 목록을 안내합니다.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛠 xLink 봇 사용 가이드",
        description="슬래시 명령어를 통해 기능을 쉽게 사용할 수 있습니다.",
        color=discord.Color.blurple()
    )
    embed.add_field(name="/채널추가", value="🎙 음성채팅방 생성
예: `/채널추가 name:듀오 user_limit:2`", inline=False)
    embed.add_field(name="/구인", value="🔗 현재 접속 중인 음성채널의 초대링크 생성
예: `/구인 duration:600`", inline=False)
    embed.add_field(name="/settarget", value="🎯 중계 대상 채널 ID 설정
예: `/settarget channel_id:1234567890`", inline=False)
    embed.add_field(name="/reinit", value="🔄 중계/음성채널 재생성", inline=False)
    embed.add_field(name="/help", value="📖 이 도움말 보기", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

peer_links = {}  # {guild_id: {"text": id, "peer_guild": id, "peer_channel": id}}

@tree.command(name="connect", description="🔗 이 서버와 상대 서버를 연합 중계합니다.")
@app_commands.describe(peer_guild_id="상대 서버 ID", peer_channel_id="상대 서버 채널 ID")
async def connect_servers(interaction: discord.Interaction, peer_guild_id: str, peer_channel_id: str):
    try:
        pgid = int(peer_guild_id)
        pcid = int(peer_channel_id)
        peer_links[interaction.guild.id] = {
            "text": relay_channels.get(interaction.guild.id, {}).get("text"),
            "peer_guild": pgid,
            "peer_channel": pcid
        }
        await interaction.response.send_message(
            f"🔗 `{peer_guild_id}` 서버와 `{peer_channel_id}` 채널로 연합 중계가 설정되었습니다.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"⚠️ 연결 실패: {e}", ephemeral=True)

@tree.command(name="disconnect", description="🔌 현재 연합 중계를 해제합니다.")
async def disconnect_server(interaction: discord.Interaction):
    if interaction.guild.id in peer_links:
        del peer_links[interaction.guild.id]
        await interaction.response.send_message("🔌 연합 중계가 해제되었습니다.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ 현재 설정된 연합이 없습니다.", ephemeral=True)


import datetime

# 로그에 기록 추가
def log_action(guild_id, action_type, peer_id):
    server = server_config.setdefault(guild_id, {"approved": [], "pending": [], "blocked": [], "log": [], "notify": True})
    server["log"].append({
        "type": action_type,
        "guild": peer_id,
        "time": datetime.datetime.now().isoformat()
    })

@bot.event
async def on_ready():
    print(f"✅ xLink 봇 작동 시작: {bot.user}")


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

