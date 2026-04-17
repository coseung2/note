# Phase 6 — pdf

**에이전트**: pdf-renderer (`agents/pdf-renderer.md`)

## 목적
HTML → PDF 렌더링 (Chromium headless).

## 입력
`phase5/notebook.html` (+ 이미지 동반 복사)

## 산출
- `phase6/notebook.pdf`
- `phase6/render.log`

## 환경
- WSL: snap chromium의 `/tmp` 제약 때문에 `/mnt/c/temp_claude/` 사용
- 한글 웹폰트 로드 위해 `--virtual-time-budget=15000` 필요

## Fallback
- Chromium 실패 → Microsoft Edge headless 재시도
- 폰트 로드 실패 → 로컬 TTF `@font-face` 대체

## 검증 게이트
- 페이지 수 일치
- 파일 크기 > 0

## 다음 phase
→ phase7 (deliver)
