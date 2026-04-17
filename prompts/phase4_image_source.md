# Phase 4 — image-source

**에이전트**: image-scout (`agents/image-scout.md`)

## 목적
교사 승인본에 따라 최종 이미지 확정. 교과서 삽화 크롭 + 외부 CC/공공 이미지 서치·다운로드.

## 입력
- `phase3/notebook_draft.approved.md`
- `phase1/image_manifest.json`, `phase1/images/`

## 산출
- `phase4/images/` — 최종 사용 이미지
- `phase4/image_map.json` — 블록ID → 이미지 매핑
- `phase4/attribution.md` — 출처·라이선스 목록

## 소싱 우선순위
1. 교과서 삽화 (학교 교육 목적)
2. 정부·공공기관 공개 자료 (국토지리정보원, 외교부 독도 누리집 등)
3. Wikimedia Commons CC
4. Unsplash / Pexels
5. **AI 생성 이미지 (폴백)** — 1~4 부적합 시. 출처 기록 불필요
6. **절대 금지**: Google 이미지 직접 다운, 블로그 이미지 무단 사용

## 검증 게이트
- 모든 체크된 블록에 이미지 파일 존재
- 외부 이미지 전부 라이선스 정보 포함

## 다음 phase
→ phase5 (render)
