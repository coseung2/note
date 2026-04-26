# Phase 1 — extract

**에이전트**: textbook-extractor (`agents/textbook-extractor.md`)

## 목적
교과서 PDF에서 전체 텍스트를 추출하고, 차시별 텍스트 파일로 분리한다.

## 입력
`tasks/{task_id}/phase0/request.json`

## 산출
- `phase1/text_all_pages.txt`
- `phase1/lesson_{NN}.txt`
- `phase1/extract.json`

## 검증 게이트
- 전체 텍스트 비어있지 않음
- lesson 파일 수 == lessons[] 수
- 각 lesson 파일이 해당 차시 페이지 범위와 일치

## 다음 phase
→ phase2 (lesson-spec)
