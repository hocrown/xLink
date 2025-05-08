# xLink Relay Bot (멀티 음성채널 + /채널추가 + /구인 명령어)
# Copyright (c) Juno / JUNOSPACE

import discord
from discord import app_commands
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
    embed.add_field(name="/채널추가", value="🎙 음성채팅방 생성\n예: `/채널추가 name:듀오 user_limit:2`", inline=False)
    embed.add_field(name="/구인", value="🔗 현재 접속 중인 음성채널의 초대링크 생성\n예: `/구인 duration:600`", inline=False)
    embed.add_field(name="/settarget", value="🎯 중계 대상 채널 ID 설정\n예: `/settarget channel_id:1234567890`", inline=False)
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

@tree.command(name="notify", description="🔔 연합 요청 발생 시 알림 설정")
@app_commands.describe(state="알림 설정: on / off")
async def notify_setting(interaction: discord.Interaction, state: str):
    state = state.lower()
    if state not in ["on", "off"]:
        await interaction.response.send_message("❌ 'on' 또는 'off' 중 하나를 입력해주세요.", ephemeral=True)
        return
    server_config.setdefault(interaction.guild.id, {"notify": True})
    server_config[interaction.guild.id]["notify"] = (state == "on")
    save_server_config()
    await interaction.response.send_message(f"🔔 알림 설정이 `{state}` 상태로 변경되었습니다.", ephemeral=True)

@tree.command(name="연결로그", description="📜 이 서버의 연합 요청/승인 로그를 조회합니다.")
async def view_logs(interaction: discord.Interaction):
    config = server_config.get(interaction.guild.id, {})
    logs = config.get("log", [])
    if not logs:
        await interaction.response.send_message("📭 기록된 연합 로그가 없습니다.", ephemeral=True)
        return
    embed = discord.Embed(title="📜 연합 로그", color=discord.Color.orange())
    for entry in logs[-10:][::-1]:  # 최신순으로 최대 10개
        ts = entry["time"].split("T")[0]
        embed.add_field(name=f"{entry['type'].upper()} - {entry['guild']}", value=f"날짜: {ts}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="block", description="⛔ 특정 서버의 연합 요청을 차단합니다.")
@app_commands.describe(guild_id="차단할 서버 ID")
async def block_server(interaction: discord.Interaction, guild_id: str):
    try:
        gid = int(guild_id)
        config = server_config.setdefault(interaction.guild.id, {"approved": [], "pending": [], "blocked": [], "log": [], "notify": True})
        if gid not in config["blocked"]:
            config["blocked"].append(gid)
            save_server_config()
            await interaction.response.send_message(f"⛔ `{gid}` 서버를 차단 목록에 추가했습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ 이미 차단된 서버입니다.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ 숫자 ID를 입력해주세요.", ephemeral=True)

@tree.command(name="연합목록", description="📋 이 봇에 연결된 연합 서버 목록을 확인합니다.")
async def list_connections(interaction: discord.Interaction):
    if not peer_links:
        await interaction.response.send_message("🔍 현재 설정된 연합 서버가 없습니다.", ephemeral=True)
        return

    embed = discord.Embed(title="🌐 xLink 연합 서버 목록", color=discord.Color.green())
    for gid, info in peer_links.items():
        name = f"서버 ID: {gid}"
        value = f"중계 채널: {info.get('text')}
연결 대상 서버: {info.get('peer_guild')}
채널 ID: {info.get('peer_channel')}"
        embed.add_field(name=name, value=value, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 중계 수정: peer_links 기반


import json
import os

CONFIG_PATH = "server_config.json"

# 서버 설정 로드
def load_server_config():
    global server_config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            try:
                server_config = json.load(f)
                print("📂 서버 설정 로드 완료")
            except json.JSONDecodeError:
                print("⚠️ server_config.json 구문 오류 - 초기화됨")
                server_config = {}
    else:
        print("📁 서버 설정 파일 없음 - 새로 생성 예정")

# 서버 설정 저장
def save_server_config():
    os.makedirs("backups", exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(server_config, f, indent=2, ensure_ascii=False)
        print("💾 서버 설정 저장 완료")

    # 자동 백업 (최대 5개 + 중복 방지)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/server_config_{timestamp}.json"

    try:
        # 중복 방지: 1분 내 파일 있으면 생략
        existing = sorted(Path("backups").glob("server_config_*.json"))
        if existing:
            last_time = existing[-1].name.split("_")[-1].split(".")[0]
            if len(last_time) == 6:
                last_time_dt = datetime.datetime.strptime(last_time, "%H%M%S")
                if (now - now.replace(hour=last_time_dt.hour, minute=last_time_dt.minute, second=last_time_dt.second)).seconds < 60:
                    print("⏱️ 최근 백업과 1분 이내여서 생략됨")
                    return

        with open(backup_file, "w", encoding="utf-8") as bf:
            json.dump(server_config, bf, indent=2, ensure_ascii=False)
            print(f"🗂️ 백업 저장됨 → {backup_file}")
        
        # 최대 5개 유지
        all_backups = sorted(Path("backups").glob("server_config_*.json"))
        if len(all_backups) > 5:
            for old in all_backups[:-5]:
                old.unlink()
                print(f"🧹 오래된 백업 삭제됨: {old}")

    except Exception as e:
        print(f"⚠️ 백업 실패: {e}")

server_config = {}  # {guild_id: {"mode": "public"/"private", "approved": [ids], "pending": [ids]}}

@tree.command(name="setmode", description="🛡 서버 연합 모드 설정 (public/private)")
@app_commands.describe(mode="공개 여부 설정: public 또는 private")
async def setmode(interaction: discord.Interaction, mode: str):
    mode = mode.lower()
    if mode not in ["public", "private"]:
        await interaction.response.send_message("❌ 'public' 또는 'private' 중 하나를 입력해주세요.", ephemeral=True)
        return
    server_config[interaction.guild.id] = server_config.get(interaction.guild.id, {})
    server_config[interaction.guild.id]["mode"] = mode
    save_server_config()
    server_config[interaction.guild.id].setdefault("approved", [])
    server_config[interaction.guild.id].setdefault("pending", [])
    await interaction.response.send_message(f"✅ 이 서버의 연합 모드가 `{mode}`로 설정되었습니다.", ephemeral=True)

@tree.command(name="connect", description="🔗 다른 서버에 연합 요청을 보냅니다.")
@app_commands.describe(peer_guild_id="상대 서버 ID", peer_channel_id="상대 서버 채널 ID")
async def connect(interaction: discord.Interaction, peer_guild_id: str, peer_channel_id: str):
    try:
        pgid = int(peer_guild_id)
        pcid = int(peer_channel_id)
        peer = server_config.get(pgid)
        if not peer:
            await interaction.response.send_message("⚠️ 대상 서버 정보가 없습니다.", ephemeral=True)
            return

        # private이면 요청 불가
        if peer["mode"] == "private":
            await interaction.response.send_message("🔒 상대 서버가 private 모드입니다. 직접 승인을 받아야 연결 가능합니다.", ephemeral=True)
            return

        # pending 요청 등록
        peer.setdefault("pending", []).append(interaction.guild.id)
        await interaction.response.send_message("⏳ 연합 요청을 보냈습니다. 상대 서버의 승인을 기다려주세요.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ 서버 ID 또는 채널 ID 형식이 잘못되었습니다.", ephemeral=True)

@tree.command(name="approve", description="✅ 연합 요청을 수락합니다.")
@app_commands.describe(guild_id="승인할 서버 ID")
async def approve(interaction: discord.Interaction, guild_id: str):
    try:
        gid = int(guild_id)
        config = server_config.setdefault(interaction.guild.id, {"approved": [], "pending": [], "mode": "private"})
        if gid in config["pending"]:
            config["pending"].remove(gid)
            config["approved"].append(gid)
            save_server_config()
            await interaction.response.send_message(f"✅ `{gid}` 서버의 요청을 승인했습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ 해당 서버의 요청이 존재하지 않습니다.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ 숫자 ID를 입력해주세요.", ephemeral=True)

@app_commands.describe(guild_id="거부할 서버 ID")
async def deny(interaction: discord.Interaction, guild_id: str):
    try:
        gid = int(guild_id)
        config = server_config.setdefault(interaction.guild.id, {"approved": [], "pending": [], "mode": "private"})
        if gid in config["pending"]:
            config["pending"].remove(gid)
            save_server_config()
            await interaction.response.send_message(f"🚫 `{gid}` 서버의 요청을 거부했습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ 해당 서버의 요청이 존재하지 않습니다.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ 숫자 ID를 입력해주세요.", ephemeral=True)

@tree.command(name="연합목록", description="📋 이 봇에 등록된 공개 연합 서버 목록을 확인합니다.")
async def union_list(interaction: discord.Interaction):
    embed = discord.Embed(title="🌐 xLink 연합 서버 목록", color=discord.Color.blurple())
    count = 0
    for gid, conf in server_config.items():
        if gid == interaction.guild.id:
            continue
        if conf.get("mode") == "public":
            approved = "✅ 연결됨" if interaction.guild.id in conf.get("approved", []) else "⏳ 승인 대기"
            embed.add_field(
                name=f"서버 ID: {gid}",
                value=f"상태: {approved}",
                inline=False
            )
            count += 1
    if count == 0:
        embed.description = "🔍 현재 연합 가능한 공개 서버가 없습니다."
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author.bot:
        return

    g_id = message.guild.id
    if g_id not in peer_links:
        return

    config = peer_links[g_id]
    if message.channel.id != config["text"]:
        return

    relay_msg = f"📡 `{message.author.display_name}`:\n{message.content}"

    try:
        peer_guild = bot.get_guild(config["peer_guild"])
        peer_channel = peer_guild.get_channel(config["peer_channel"]) if peer_guild else None
        if peer_channel:
            await peer_channel.send(relay_msg)
    except Exception as e:
        print(f"중계 실패: {e}")

@bot.event
async def on_ready():
    load_server_config()
    print(f"✅ xLink 봇 작동 시작: {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🔧 {len(synced)}개의 슬래시 커맨드 등록 완료")
    except Exception as e:
        print(f"❌ 슬래시 커맨드 등록 실패: {e}")

async def setup_guild(guild: discord.Guild):
    text_channel = await guild.create_text_channel("xlink-중계")
    relay_channels[guild.id] = {
        "text": text_channel.id,
        "target": None
    }
    await text_channel.send("✅ xLink 중계 채널이 생성되었습니다.")

@bot.event
async def on_guild_join(guild):
    try:
        await setup_guild(guild)
    except discord.Forbidden:
        print(f"❌ {guild.name} 서버에서 채널 생성 권한 없음")

@tree.command(name="채널추가", description="📢 음성채팅방을 새로 생성합니다 (최대 인원 지정 가능)")
@app_commands.describe(name="채널 이름", user_limit="최대 인원 (0은 제한 없음)")
async def create_voice_channel(interaction: discord.Interaction, name: str, user_limit: int = 0):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ 채널을 생성할 권한이 없습니다.", ephemeral=True)
        return
    try:
        new_channel = await interaction.guild.create_voice_channel(name=name, user_limit=user_limit)
        await interaction.response.send_message(f"✅ 음성채널 `{name}` (최대 {user_limit}명)을 생성했습니다.")
    except Exception as e:
        await interaction.response.send_message(f"⚠️ 채널 생성 중 오류: {e}", ephemeral=True)

@tree.command(name="settarget", description="🎯 상대 서버의 중계 채널 ID를 등록합니다.")
@app_commands.describe(channel_id="중계할 대상 채널의 ID")
async def settarget(interaction: discord.Interaction, channel_id: str):
    try:
        cid = int(channel_id)
        if interaction.guild.id not in relay_channels:
            relay_channels[interaction.guild.id] = {"text": None, "target": cid}
        else:
            relay_channels[interaction.guild.id]["target"] = cid
        await interaction.response.send_message(f"✅ 타겟 채널이 `{cid}`로 설정되었습니다.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("❌ 숫자 채널 ID를 입력해주세요.", ephemeral=True)

@tree.command(name="구인", description="🔗 현재 접속 중인 음성채팅방 초대 링크를 생성합니다.")
@app_commands.describe(duration="초대 링크 유효 시간 (초)")
async def generate_voice_invite(interaction: discord.Interaction, duration: int = 3600):
    member = interaction.user
    vc = member.voice.channel if member.voice else None

    if not vc:
        await interaction.response.send_message("⚠️ 현재 음성 채널에 접속 중이 아닙니다.", ephemeral=True)
        return

    try:
        invite = await vc.create_invite(max_age=duration, max_uses=5, unique=True)
        await interaction.response.send_message(
            f"🔊 `{vc.name}` 음성채널 구인 링크입니다:
👉 [입장하기]({invite.url})
⏱ 유효시간: {duration}초"
        )
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ 초대 링크 생성 권한이 없습니다.", ephemeral=True)


