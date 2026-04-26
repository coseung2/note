# Phase 3 — draft-board

**에이전트**: draft-board-builder (`agents/draft-board-builder.md`)

## 목적
phase2 JSON을 차시별 드래프트 공책보드 PNG/PDF로 렌더한다.

## 입력
- `phase0/request.json`
- `phase2/notebook.json`
- `phase2/notebook_{NN}.json`

## 산출
- `phase3/lesson_{NN}.html`
- `phase3/lesson_{NN}.png`
- `phase3/lesson_{NN}.pdf`
- `phase3/board_manifest.json`

## 규칙
- 차시당 1장
- 실제 이미지 사용 금지
- 이미지 위치에는 프레임 상자 + 설명문 삽입
- 텍스트 가독성이 최우선

## 검증 게이트
- 모든 차시에 PNG 생성
- 프레임 설명이 눈으로 읽힘
- phase4 레퍼런스로 바로 쓸 수 있는 수준

## 다음 phase
→ phase4 (stylize)
