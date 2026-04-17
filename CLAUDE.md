# note — 교과서 → 학생 공책정리 PDF 생성 프로젝트

이 폴더는 **초등 교과서 PDF를 입력받아 학생 공책 스타일의 단원별 완성 정리본 PDF를 자동 생성**하는 파이프라인의 프로덕션 워크스페이스다.

> 이 프로젝트는 `ideation/notebook-workflow/`에서 정교화된 워크플로우를 이식한 것이다. 의사결정 이력·리서치·로드맵은 `plans/`, `research/`에 동반 이식됨.

## 원칙

1. **에이전트 기반 파이프라인** — 8 phase, 각 phase 전담 서브에이전트
2. **교사 검증 게이트 필수** — phase3에서 교사가 draft.md를 직접 편집·승인
3. **이미지 소싱 우선순위** — ① 교과서 삽화 → ② 공공/CC → ③ AI 생성 이미지 (폴백, 상위 후보가 없을 때만)
4. **저작권 메타** — 외부 실사 이미지는 출처·라이선스 기록 필수 (`attribution.md`). AI 생성 이미지는 기록 불필요
5. **OneDrive 배송** — `OneDrive - 남선초등학교\학습자료\{과목}\공책정리\` 표준 경로
6. **이식성 우선** — Docker 없이 WSL2 단일 환경에서 완결

## 오케스트레이터 프로토콜

메인 세션은 직접 PDF 처리·LLM 호출·HTML 편집·렌더링을 하지 않는다. 각 phase를 전담 에이전트에 `Agent` 도구로 위임한다.

### Phase ↔ 에이전트 매핑

| Phase | 에이전트 | 주력 도구 |
|---|---|---|
| 0 intake | intake-analyst | PyMuPDF |
| 1 extract | textbook-extractor | PyMuPDF + Claude Vision |
| 2 draft | content-curator | Claude Tool Use (JSON schema) |
| 4 image-source | image-scout | Pillow + Wikimedia API |
| **4.5 review** | **reviewer** | PIL + CSS 파서 + Vision (선택) |
| **3 validate** | **교사 수동 최종 승인** | 브라우저 preview.html |
| 5 render | html-builder | Jinja2 + mistune |
| 6 pdf | pdf-renderer | Playwright Chromium |
| 7 deliver | dispatcher | PowerShell interop |

> **Phase 3은 4.5 다음에 수행** — 자동 리뷰로 걸러진 결과를 교사가 최종 승인 (2026-04-15 순서 변경).

### 호출 포맷

```
Agent({
  description: "Phase {N} — {agent-name}",
  subagent_type: "general-purpose",
  prompt: "<agents/{agent-name}.md 전문>\n\n---\n런타임 입력:\n- task_id: {YYYY-MM-DD-slug}\n- 입력 파일: {prev_phase_output}\n- 추가 맥락: ..."
})
```

### 오케스트레이터가 직접 하는 일

- `tasks/{task_id}/phase{N}/` 폴더 생성
- 검증 게이트 판정 (각 phase 완료 시)
- phase 간 파일 경로 전달
- 재시도 결정 (실패 시 최대 3회)
- 사용자 커뮤니케이션 (draft 검증 요청, 이미지 선택 에스컬레이션)
- 에이전트가 유보한 항목(`_questions.md`)을 사용자에게 질문

### 오케스트레이터가 하지 않는 일

- 직접 pdftotext·pdfimages·chromium 실행
- 직접 HTML 편집·이미지 서치
- 에이전트 산출물 수정 (재호출로 해결)

## 파이프라인 흐름

```
[0] intake → [1] extract → [2] draft → [4] image-source →
    [4.5] review → ⏸ [3] validate (교사 최종 승인) → [5] render → [6] pdf → [7] deliver
```

상세 사양: `prompts/_index.md`
에이전트 계약서: `agents/_registry.md`

## 검증 게이트

| 게이트 | 위치 | 통과 조건 |
|---|---|---|
| 입력완비 | phase0 직후 | request.json 필수 필드 + PDF 실재 |
| 추출성공 | phase1 직후 | text 추출 + images 디렉토리 비어있지 않음 |
| 드래프트완성 | phase2 직후 | 모든 페이지 블록 ≥ 3 + 이미지 후보 ≥ 1 |
| **교사승인** | phase3 직후 | `status: approved` 프론트매터 + 변경 타임스탬프 갱신 |
| 이미지확정 | phase4 직후 | image_map.json 모든 경로가 실재 파일 |
| 렌더성공 | phase5 직후 | HTML valid + 이미지 해석 |
| PDF완성 | phase6 직후 | A4 + 페이지 수 일치 |
| 배송완료 | phase7 직후 | OneDrive 복사본 + sha256 일치 |

실패 시 해당 phase 재실행. 3회 연속 실패 시 사용자에게 보고.

## 디렉토리

```
note/
├── CLAUDE.md              # 이 파일 — 오케스트레이션 헌법
├── README.md              # 프로젝트 소개·사용법
├── INDEX.md               # 전체 산출물 인덱스
├── SETUP.md               # 환경 설치 (Python·apt·폰트·환경변수)
├── template.html          # 재사용 HTML/CSS 스켈레톤
├── agents/                # 8개 에이전트 계약서
│   ├── _registry.md
│   ├── intake-analyst.md
│   ├── textbook-extractor.md
│   ├── content-curator.md
│   ├── image-scout.md
│   ├── html-builder.md
│   ├── pdf-renderer.md
│   └── dispatcher.md
├── prompts/               # phase 사양
│   ├── _index.md
│   └── phase{0..7}_*.md
├── tasks/                 # 실행 이력 (감사용)
│   └── {YYYY-MM-DD-slug}/
│       ├── phase0~7/
│       └── DELIVERED.md
├── plans/                 # 살아있는 문서
│   └── roadmap.md         # v1~v6 로드맵·의사결정 이력
├── research/              # 리서치 보고서
│   └── notebook-generation-from-textbook-research.md
├── examples/              # 참고 예시
│   └── social-5-1-unit1.html  # v1 수동 작성 샘플
└── INBOX/                 # ideation dispatcher가 보내는 요청
    └── README.md
```

## 자율 진행 방침

- 사용자가 "쭉 진행해" 지시한 상태가 기본
- LLM 1차(phase2 draft) 자동 진행, 검증(phase3)은 사용자 필수 개입
- 외부 이미지 서치 결과 모호할 때만 사용자 확인 (그 외 자율 판단)
- 파일 생성·수정(note 내부) 자유. ideation 외부 폴더는 **OneDrive 배송 경로만** 쓰기 허용

## 상위 컨텍스트

- 이 프로젝트는 `ideation/`에서 출발했음. 의사결정 이력·이전 실험 산출물은 ideation 기록 참조
- ideation의 dispatcher가 새 요청을 보낼 때 `note/INBOX/`로 들어옴 (`INBOX/README.md` 참조)

## 메모리 참조

사용자 방침은 ideation의 메모리 시스템 (`/home/coseung2/.claude/projects/-mnt-c-Users-----Desktop-Obsidian-Vault-ideation/memory/MEMORY.md`)에 저장됨. 주요 항목:
- `feedback_notebook_style.md` — 학생 필기 스타일 원칙
- `feedback_no_ai_doodles.md` — AI 손그림 금지, 실제 이미지만
- `project_baseline_device.md` — 갤탭 S6 Lite 기준 (태블릿 열람 시)
- `feedback_quality_over_devcost.md` — 품질 우선
