# Phase 2 — draft

**에이전트**: content-curator (`agents/content-curator.md`)

## 목적
교과서 원문·삽화 카탈로그 → 교사 검토용 `notebook_draft.md` 생성. **교사가 읽고 체크박스 토글·수정할 수 있는 형태**.

## 입력
- `phase0/request.json`
- `phase1/text_by_page/*.txt`
- `phase1/image_manifest.json`

## 산출
- `phase2/notebook_draft.md` (프론트매터 `status: draft`)
- `phase2/image_candidates.json`

## 필수 포함 섹션
1. 페이지별 학습목표·키워드:설명·callout·말풍선·이미지 후보·한문장 정리
2. 🗑 "LLM이 뺐지만 교사가 복구 가능" 섹션
3. 📝 "교사 추가 지시" 자유 텍스트 영역

## 선별 원칙
- 교과서 본문 어휘 우선, AI 창작 금지
- 페이지당 블록 3~6개
- 이미지는 교과서 삽화 우선, 부족 시 `external:search:{query}` 마커

## 검증 게이트
- 모든 페이지 블록 ≥ 3
- 모든 페이지 이미지 후보 ≥ 1

## 다음 phase
→ phase3 (교사 검증)
