# Phase 7 — deliver

**에이전트**: dispatcher (`agents/dispatcher.md`)

## 목적
완성 PDF를 OneDrive 경로로 배송 + 배송 기록.

## 입력
- `phase0/request.json` (delivery_path)
- `phase6/notebook.pdf`
- `phase4/attribution.md`

## 산출
- OneDrive 경로에 PDF 복사
- `DELIVERED.md` (배송 기록)

## 파일명 규칙
`{과목}{학년}-{학기}_{단원번호}단원_공책정리본.pdf`
재실행 시 `_v2`, `_v3` 접미사 (기존 보존)

## 검증 게이트
- OneDrive 경로에 복사본 존재 + 크기 일치
- DELIVERED.md 생성

## 실패 처리
- OneDrive 프로세스 중지 → 사용자에게 "실행 후 재시도" 요청
- 폴더 없음 → 자동 생성
