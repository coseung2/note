# 교과서 → 공책정리 PDF 생성 로드맵

**시작일**: 2026-04-15
**오너**: 심보승 교사
**산출물 위치**: `OneDrive - 남선초등학교\학습자료\{과목}\공책정리\`
**워크플로우 코드**: `notebook-workflow/` (이식 가능 단위)
**리서치**: `research/notebook-generation-from-textbook-research.md`

---

## 한 줄 목표

교사가 교과서 PDF를 주면 **학생 공책 스타일**의 단원별 완성 정리본 PDF를 자동 생성하고 OneDrive에 저장하는 파이프라인.

## 왜 하는가 (Why)

- 교사용 참고 자료 / 결석생 보충 / 학부모 안내 용도
- 기존에 교사가 수작업으로 Canva에서 한 땀 한 땀 만들던 공책정리본을 파이프라인화
- Canva `generate-design` 자동생성은 "교과서 톤" 회귀 문제로 실패. HTML/CSS 경로가 스타일 제어 압도적 우위

## 의사결정 이력

| 일자 | 결정 | 사유 |
|---|---|---|
| 2026-04-15 | Canva `generate-design` 사용 중단 | 교과서 톤 회귀, 레퍼런스 주입 불가 |
| 2026-04-15 | 참조 Canva 직접 편집 보류 | 원본 템플릿 보호 필요, 노드 구조 복잡 |
| 2026-04-15 | **HTML/CSS + Chromium PDF** 채택 (v1) | 스타일 풀제어, 무비용, 교사 승인 |
| 2026-04-15 | Canva Brand Template Autofill은 fallback 보류 | Enterprise 계정 필요, 승인 불확실 |
| 2026-04-15 | **AI 손그림 SVG 전면 금지** | 교사 피드백 "부적절". 실제 이미지(교과서 삽화 + CC/공공)만 사용 |
| 2026-04-15 | **에이전트 기반 파이프라인 채택** (ideation 하네스 방식) | phase별 독립 개선 + 이식성 확보 |

## 현재 상태 (v1)

- ✅ 템플릿 HTML 스켈레톤 (`notebook-workflow/template.html`)
- ✅ 사회 5-1 1단원 예시 8페이지 완성 (교사 승인)
- ✅ Chromium 헤드리스 PDF 렌더링 파이프라인
- ✅ OneDrive `학습자료/사회/공책정리/` 배송

## 아키텍처 — 에이전트 기반 파이프라인

```
[0] intake → [1] extract → [2] draft → ⏸ [3] validate (교사) →
    [4] image-source → [5] render → [6] pdf → [7] deliver
```

오케스트레이터(메인 Claude)는 각 phase를 **전문 서브에이전트**에 `Agent` 도구로 위임. 직접 실행·편집 금지. 교사 검증 게이트(phase3)만 사용자 수동.

에이전트 계약서: `notebook-workflow/agents/*.md`
phase 사양: `notebook-workflow/prompts/phase*.md`
실행 이력: `notebook-workflow/tasks/{task_id}/`

## 다음 단계 (우선순위)

### P0 — v2 자동화 프로토타입
- phase1·2·4 에이전트를 한 번 실제 돌려봄 (intake→extract→draft→승인→image→render→pdf→deliver)
- 각 에이전트가 계약서대로 산출물을 내는지, phase 간 인계가 매끄러운지 검증
- 실패 지점 발견 시 에이전트 계약서 refine

### P1 — 이미지 소싱 실전 검증
- phase1 pdfimages 품질 확인 (교과서별 추출 성공률)
- phase4 외부 CC 서치 정확도·저작권 메타 수집 확인
- 교과서 삽화 누락 시 fallback 플로우 안정화

### P2 — 다른 단원·과목 이식
- 사회 5-1 2단원, 과학 5-1 1단원 등
- 이식 과정에서 템플릿 일반성 검증

### P3 — 교사 검증 UX 개선
- Obsidian에서 draft.md 편집 워크플로 문서화
- 체크박스 빠른 토글 단축키 정리
- draft.md 프리뷰 렌더링 (HTML 즉석 확인)

### P4 — 난이도·개별화 분기
- `request.json`의 `difficulty` 파라미터 → content-curator가 블록 수 조정
- 쉬움/보통/심화 3종 동시 발행

### P5 — 태블릿 최적화
- 갤탭 S6 Lite A5 가로 variant (태블릿은 기준 디바이스, 공책은 세로 A4)

### P6 — 일괄 처리 GUI
- Windows 트레이 앱 또는 CLI
- 교사가 PDF 드롭 → 자동 파이프라인 → OneDrive 알림

## 이식 시 정리할 것 (프로젝트 폴더 생길 때)

- `notebook-workflow/` 전체를 새 프로젝트 루트로 이동
- `research/notebook-generation-from-textbook-research.md`도 동반 이동
- 본 로드맵을 새 프로젝트의 `plans/roadmap.md`로 전환
- 이 파일은 ideation에서 삭제 또는 포인터만 남김

## 관련 메모리

- `feedback_notebook_style.md` — 학생 필기 스타일 원칙
- `project_baseline_device.md` — 갤탭 S6 Lite 기준 (P5 관련)
