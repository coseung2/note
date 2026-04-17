# Agent: dispatcher

**Phase**: 7 — deliver
**역할**: PDF를 OneDrive 경로로 배송 + 동기화 검증 + 교사 알림.

## 파일명 규칙 (2026-04-15 교사 피드백)

각 차시 PDF는 **교과서 레벨 + 단원번호 + 차시번호 + 차시 제목**을 포함:

```
{과목}{학년}-{학기}_{단원}_{NN}차시_{lesson_title}.pdf
예: 사회5-1_1단원_03차시_우리나라의 하천.pdf
```

- `NN`은 2자리 (01, 02, ... 10) — 정렬 유지
- `lesson_title`은 `notebook_{NN}.json`의 `lesson_title` 그대로
- 파일명 내 금지 문자(`/ \ : * ? " < > |`)는 `_`로 치환

## 입력

- `phase0/request.json` (delivery_path, 파일명 힌트)
- `phase6/notebook.pdf`
- `phase4/attribution.md`

## 산출

- OneDrive 경로에 PDF 복사
- `phase7/manifest.sha256` (체크섬 체인)
- `DELIVERED.md` (배송 기록)

## Primary Tool

**PowerShell via WSL interop + sha256sum** — 추가 설치 없음, Windows ↔ WSL 교차 호출.

## 핵심 코드

```bash
#!/bin/bash
set -euo pipefail

TASK_ID="2026-04-15-social-5-1-unit1"
TITLE="사회5-1_1단원_공책정리본"
OUT="tasks/$TASK_ID/phase6/notebook.pdf"
ONEDRIVE="/mnt/c/Users/심보승/OneDrive - 남선초등학교"
DEST_DIR="$ONEDRIVE/학습자료/사회/공책정리"
mkdir -p "$DEST_DIR"

# 1) 파일명 중복 회피 (v2, v3 suffix)
DEST="$DEST_DIR/${TITLE}.pdf"
i=2
while [ -e "$DEST" ]; do
  DEST="$DEST_DIR/${TITLE}_v${i}.pdf"
  i=$((i+1))
done

# 2) 복사 + 체크섬
cp "$OUT" "$DEST"
SHA=$(sha256sum "$DEST" | awk '{print $1}')
echo "$SHA $DEST" >> "tasks/$TASK_ID/phase7/manifest.sha256"

# 3) OneDrive 동기화 프로세스 확인
ONEDRIVE_RUNNING=$(powershell.exe -NoProfile -Command \
  "if (Get-Process OneDrive -ErrorAction SilentlyContinue) { 'yes' } else { 'no' }" | tr -d '\r\n')

if [ "$ONEDRIVE_RUNNING" = "no" ]; then
  echo "⚠️  OneDrive 프로세스 중지. 자동 실행 시도..."
  powershell.exe -Command "Start-Process 'C:\\Users\\심보승\\AppData\\Local\\Microsoft\\OneDrive\\OneDrive.exe'"
fi

# 4) "항상 유지" 속성 강제 (cloud-only 회피)
WIN_DEST=$(wslpath -w "$DEST")
powershell.exe -Command "attrib.exe -U +P '$WIN_DEST'" 2>/dev/null || true

# 5) 교사 토스트 알림
powershell.exe -Command "
Add-Type -AssemblyName System.Windows.Forms;
[System.Windows.Forms.MessageBox]::Show(
  '공책정리 PDF 생성 완료:`n$TITLE`n`n저장 위치: $WIN_DEST',
  '공책정리 Pipeline','OK','Information')" >/dev/null 2>&1 &
```

## 파일명 규칙

```
{과목}{학년}-{학기}_{단원번호}단원_공책정리본{_v{version}}.pdf

예: 사회5-1_1단원_공책정리본.pdf
재실행: 사회5-1_1단원_공책정리본_v2.pdf (기존 보존, 덮어쓰기 금지)
```

## DELIVERED.md 스키마

```markdown
---
task_id: 2026-04-15-social-5-1-unit1
delivered_at: 2026-04-15T11:45:00+09:00
sha256: abc123...
---

# 배송 완료

- **파일**: `OneDrive - 남선초등학교\학습자료\사회\공책정리\사회5-1_1단원_공책정리본.pdf`
- **크기**: 1.05 MB
- **페이지**: 8
- **SHA256**: `abc123...`

## 산출 경로

- PDF: 위 경로
- HTML 원본: `tasks/2026-04-15-social-5-1-unit1/phase5/notebook.html`
- 이미지 출처: `tasks/2026-04-15-social-5-1-unit1/phase4/attribution.md`

## 저작권 고지

학교 교육 목적 이용. 대외 배포 시 attribution.md 동반 필수.
```

## 동기화 검증

```powershell
# OneDrive 파일 속성으로 로컬 동기화 상태 판별
# 'Offline' 속성 없으면 로컬 동기화 완료
(Get-Item "...\note.pdf").Attributes
```

## 알림 대안

- **Windows toast** (위 코드)
- **Slack webhook**: `curl -X POST -H 'Content-type: application/json' --data '{"text":"PDF 완료"}' "$SLACK_URL"`
- **Gmail SMTP**: `msmtp` 또는 `ssmtp` 한 줄 설정

## 허용 도구

`Bash` (cp, sha256sum, mkdir, wslpath, powershell.exe, attrib.exe), `Read`, `Write`

## 검증 게이트

- OneDrive 경로에 복사본 존재 + 크기 일치 (cmp -s 확인)
- sha256 체인 기록
- DELIVERED.md 생성
- 파일명 규칙 준수

## 실패 처리

- OneDrive 프로세스 중지 → 자동 실행 시도, 실패 시 사용자에 토스트로 "OneDrive 실행 후 재시도" 표시
- 폴더 없음 → `mkdir -p` 자동 생성
- 동일 파일명 기존 존재 → v2, v3 suffix 자동 증가 (덮어쓰기 금지 원칙)
- 한글 파일명 cp949 깨짐 → WSL UTF-8 유지 + `$OutputEncoding=[Text.UTF8Encoding]::new()`
- 학교망 OneDrive 차단 → 로컬 `~/synced/` 미러 후 퇴근 후 개인망에서 sync

## 참고

- https://learn.microsoft.com/en-us/windows/wsl/interop
- https://learn.microsoft.com/en-us/onedrive/developer/
