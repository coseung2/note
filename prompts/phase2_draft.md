# Phase 2 — lesson-spec

**에이전트**: content-curator (`agents/content-curator.md`)

## 목적
차시별 원문 텍스트를 공책정리용 구조화 JSON으로 바꾼다.

## 입력
- `phase0/request.json`
- `phase1/lesson_{NN}.txt`
- `phase1/extract.json`

## 산출
- `phase2/notebook.json`
- `phase2/notebook_{NN}.json`

## 필수 포함 요소
1. 차시명
2. 핵심 개념 블록 3개 이상
3. 이미지 자리 프레임에 들어갈 설명문(`image_frame_prompt`)
4. 필요 시 한 문장 정리 / 빈칸 정리

## 검증 게이트
- 모든 차시에 blocks ≥ 3
- 시각 요소가 필요한 카드에는 `image_frame_prompt` 존재
- 텍스트만으로 이해 가능한 요약 구조

## 다음 phase
→ phase3 (draft-board)
