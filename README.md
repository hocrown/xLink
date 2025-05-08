# xLink - Discord Relay Bot

> PUBG 클랜 간 구인/구직 채널을 실시간 연결하는 디스코드 중계 봇  
> Copyright (c) Juno / JUNOSPACE

---

## 🔍 개요

**xLink**는 PUBG를 중심으로 활동하는 Discord 서버 간에  
지정된 채널의 메시지를 실시간으로 감지하고, **다른 서버로 중계 전송**하는 자동화 봇입니다.
연합 서버를 위해 여러 서버간 구인/구직을 간편하게 하기 위해 개발을 시작했습니다. 향후 다양한 확장 기능도 탑재될 예정입니다.

---

## 🚀 주요 기능

- ✅ 특정 채널에서의 메시지를 **실시간 중계**
- ✅ 채널 간 전송 메시지 포맷 커스터마이징
- ✅ 채널 간 구인/구직 및 음성채널 참여
- ✅ Docker 기반으로 **24/7 서버 운영 가능**

---

## 🧩 설치 및 실행 가이드

### 1. 봇 등록 및 초대
- [Discord Developer Portal](https://discord.com/developers/applications)에서 봇 생성
- 토큰 발급 및 서버 권한 부여 후, 대상 두 서버에 초대

### 2. 환경 변수 설정 (`.env`)
```env
DISCORD_TOKEN=your-bot-token
