# Phase 5 — render

**에이전트**: html-builder (`agents/html-builder.md`)

## 목적
승인 draft + 확정 이미지 → `template.html` 주입 → 완성 HTML.

## 입력
- `phase3/notebook_draft.approved.md`
- `phase4/image_map.json`, `phase4/images/`
- `../../template.html` (스켈레톤)

## 산출
- `phase5/notebook.html`
- (선택) `phase5/notebook.standalone.html` — 이미지 base64 임베드

## 규칙
- 체크된 `- [x]` 항목만 반영
- 🗑 섹션 무시
- 📝 교사 지시는 해석해서 스타일 조정 가능
- template.html의 CSS 수정 금지
- **AI 자체 SVG 도안 생성 금지** — 이미지는 phase4 결과만 사용

## 검증 게이트
- 이미지 src 경로 전부 실재 파일
- 페이지 수 == draft 페이지 수

## 다음 phase
→ phase6 (pdf)
