# xLink - Discord Relay Bot (Private Server Mode)

> 실시간 Discord 서버 간 중계 및 연합 시스템 (Private 전용)
>
> Copyright (c) Juno / JUNOSPACE

## 🧩 소개
xLink는 PUBG 또는 클랜 기반 Discord 서버 간의 구인/구직 정보를 **연합 서버 간 실시간 중계**하는 봇입니다.  
특히 **Private 모드**를 중심으로, 승인된 서버 간에만 중계를 허용하고, 음성채널 초대/차단/로그 등을 지원합니다.

## 🚀 주요 기능

### ✅ 연합 시스템 (Private 기반)
- `/setmode private`으로만 설정 가능 (기본값도 private)
- `/connect` → 연합 요청
- `/approve`, `/deny` → 연합 승인/거부
- `/연합목록` → 현재 연합 요청 현황 표시 (Embed)

### 🔐 관리 기능
- `/block` → 특정 서버의 연합 요청 차단
- `/notify on/off` → 연합 요청 발생 시 알림 여부 설정
- `/연결로그` → 승인/요청/차단 내역 최근 10개 확인 가능

### 🎙 음성 초대 기능
- `/구인` → 현재 접속 중인 음성채널 초대링크 생성
- `/채널추가 name:이름 user_limit:N` → 음성 채널 관리자 생성

### 💾 저장 및 백업
- 모든 설정은 `server_config.json`에 저장됨
- 설정 변경 시마다 자동 저장 + `/backups/` 폴더에 최대 5개까지 백업 유지

---

## 🛠 설치 방법

### 1. `.env` 파일 작성
```
DISCORD_TOKEN=your-bot-token
```

### 2. Docker 빌드 및 실행
```bash
docker build -t xlink-bot .
docker run -d --name xlink --env-file .env xlink-bot
```

> Docker는 기본적으로 `/app/server_config.json`에 설정을 저장합니다.

---

## 📂 프로젝트 구조
```
xlink-bot/
├── xlink.py                # 봇 메인 코드
├── .env                    # Discord Bot Token
├── server_config.json      # 서버 설정 저장소
├── backups/                # 자동 백업 디렉토리
├── Dockerfile
└── requirements.txt
```

---

## 📈 향후 확장 예정
- ✅ `/복원 [파일명]` 기능
- 🔜 Public 모드 연합 목록 자동 매칭
- 🔜 웹 기반 설정 GUI (Webhook 또는 DB 연동)
- 🔜 서버 간 인증 토큰 방식 추가

---

## 👤 Contributors
- **Juno** — 전체 설계 및 개발
- **JUNOSPACE** — 운영/배포/기획

## 📄 라이선스
MIT License (with attribution)  
Copyright (c) Juno / JUNOSPACE
