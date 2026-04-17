# note — 교과서 → 학생 공책정리 PDF

초등 교과서 PDF를 입력받아 **학생이 직접 필기한 것 같은 스타일**의 단원별 공책정리 PDF를 자동 생성하는 파이프라인.

## 빠른 시작

```bash
# 1. 환경 설치
cat SETUP.md  # 의존성 설치 가이드

# 2. 새 작업 시작 (Claude Code에서)
# "사회 5-1 1단원 교과서 공책정리 만들어줘. PDF는 ~/Downloads/social5-1.pdf"
# → 오케스트레이터가 phase0부터 자동 진행
# → phase3 교사 검증 단계에서 일시 정지 (draft.md 편집 요청)
# → 승인하면 자동으로 phase4~7 진행
# → 완성 PDF가 OneDrive 학습자료 폴더에 배송됨
```

## 파이프라인

```
[0] intake → [1] extract → [2] draft → ⏸ [3] validate (교사) →
    [4] image-source → [5] render → [6] pdf → [7] deliver
```

| Phase | 담당 | 주력 도구 |
|---|---|---|
| 0 intake | intake-analyst | PyMuPDF |
| 1 extract | textbook-extractor | PyMuPDF + Claude Vision |
| 2 draft | content-curator | Claude Tool Use |
| **3 validate** | **교사 수동** | Obsidian + Tasks 플러그인 |
| 4 image-source | image-scout | Pillow + Wikimedia API |
| 5 render | html-builder | Jinja2 + mistune |
| 6 pdf | pdf-renderer | Playwright Chromium |
| 7 deliver | dispatcher | PowerShell interop |

## 핵심 원칙

1. **학생 공책 스타일** — 교과서 발췌형 ✗, `핵심키워드 : 짧은설명 + 간단그림` ○
2. **교사 검증 필수** — LLM이 고른 콘텐츠를 교사가 체크박스로 토글·수정
3. **이미지 소싱 우선순위** — 교과서 삽화 → 공공/CC → AI 생성 이미지(폴백, 3개 안 중 교사 선택)
4. **저작권 기록** — 외부 실사 이미지는 `attribution.md`에 출처·라이선스 (AI 생성분은 불필요)
5. **OneDrive 배송** — 교사 컴퓨터에서 즉시 활용

## 문서 진입점

| 누구 | 어디부터 |
|---|---|
| 처음 보는 사람 | `README.md` (이 파일) → `CLAUDE.md` |
| 환경 설치 | `SETUP.md` |
| 새 작업 시작 | Claude Code에 자연어로 요청 (오케스트레이터가 phase0 시작) |
| 워크플로우 수정 | `agents/{이름}.md` 또는 `prompts/phase{N}_*.md` |
| 로드맵 확인 | `plans/roadmap.md` |
| 리서치 배경 | `research/notebook-generation-from-textbook-research.md` |
| 예시 결과 | `examples/social-5-1-unit1.html` |

## 상태

- ✅ v1 (수동 HTML) 동작 — 사회 5-1 1단원 샘플
- 🚧 v2 (LLM 자동화) 설계 완료, 프로토타입 진입 대기
- 🚧 다른 단원·과목 이식 검증 대기

자세한 로드맵: `plans/roadmap.md`
