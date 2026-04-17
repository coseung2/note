# Phase 1 — extract

**에이전트**: textbook-extractor (`agents/textbook-extractor.md`)

## 목적
교과서 PDF에서 본문 텍스트와 삽화를 분리 추출해 구조화된 형태로 저장.

## 입력
`tasks/{task_id}/phase0/request.json`

## 산출
- `phase1/text.txt` — pdftotext 전체
- `phase1/text_by_page/p{NNN}.txt` — 페이지별 분할
- `phase1/images/` — pdfimages 추출본
- `phase1/image_manifest.json` — 이미지 카탈로그 (content_type_hint, usable 플래그)

## 검증 게이트
- text 비어있지 않음
- images 디렉토리 파일 ≥ 1
- manifest와 실제 파일 일치

## 사용 도구
`pdftotext`, `pdfimages`, `pdfinfo`, `identify`(ImageMagick)

## 다음 phase
→ phase2 (draft)
