# note — 교과서 → 학생 공책정리 PDF 생성 프로젝트

이 폴더는 **초등 교과서 PDF를 입력받아 학생 공책 스타일의 차시별 완성 정리본 PNG/PDF를 자동 생성**하는 파이프라인의 프로덕션 워크스페이스다.

> 이 프로젝트는 `ideation/notebook-workflow/`에서 정교화된 워크플로우를 이식한 것이다. 의사결정 이력·리서치·로드맵은 `plans/`, `research/`에 동반 이식됨.

## 원칙

1. **에이전트 기반 파이프라인** — 6 phase, 각 phase 전담 서브에이전트
2. **무인 기본 흐름** — 중간 사용자 검수 없이 끝까지 진행한다. 품질 이상 징후가 있을 때만 사용자 확인으로 에스컬레이션
3. **텍스트 정확도 우선** — phase2/3는 교과서 내용을 정확히 요약하고, phase4는 스타일 변환만 수행한다. 사실 추가·삭제 금지
4. **이미지 전략 변경** — phase3에서는 실제 이미지를 꽂지 않고, 이미지가 들어갈 자리 프레임과 설명문을 만든다. phase4에서 `ima2`가 이를 최종 공책 스타일 이미지로 변환한다
5. **OneDrive 배송** — `OneDrive - 남선초등학교\학습자료\{과목}\공책정리\` 표준 경로
6. **이식성 우선** — Docker 없이 WSL2 단일 환경에서 완결

## 오케스트레이터 프로토콜

메인 세션은 직접 PDF 처리·LLM 호출·HTML 편집·렌더링을 하지 않는다. 각 phase를 전담 에이전트에 `Agent` 도구로 위임한다.

### Phase ↔ 에이전트 매핑

| Phase | 에이전트 | 주력 도구 |
|---|---|---|
| 0 intake | intake-analyst | PyMuPDF |
| 1 extract | textbook-extractor | PyMuPDF |
| 2 lesson-spec | content-curator | Claude Tool Use (JSON schema) |
| 3 draft-board | draft-board-builder | Jinja2 + Playwright |
| 4 stylize | ima2-stylizer | `ima2` CLI/UI |
| 5 deliver | dispatcher | PowerShell interop |

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
[0] intake → [1] extract → [2] lesson-spec → [3] draft-board →
    [4] stylize (ima2) → [5] deliver
```

상세 사양: `prompts/_index.md`
에이전트 계약서: `agents/_registry.md`
기존 HTML/CSS+PDF 중심 flow는 legacy(v1)로 간주한다.

## 검증 게이트

| 게이트 | 위치 | 통과 조건 |
|---|---|---|
| 입력완비 | phase0 직후 | request.json 필수 필드 + PDF 실재 + 스타일 레퍼런스 경로 존재 |
| 추출성공 | phase1 직후 | 차시별 텍스트 청크 생성 + lessons[] 수 일치 |
| 스펙완성 | phase2 직후 | 모든 차시에 제목·핵심 블록·이미지 프레임 설명 ≥ 1 |
| 드래프트보드완성 | phase3 직후 | 차시별 PNG/PDF 생성 + 텍스트 가독성 확보 |
| 스타일변환성공 | phase4 직후 | 차시별 최종 PNG 존재 + `ima2` 실행 로그 정상 |
| 배송완료 | phase5 직후 | OneDrive 복사본 + sha256 일치 |

실패 시 해당 phase 재실행. 3회 연속 실패 시 사용자에게 보고.

## 디렉토리

```
note/
├── CLAUDE.md              # 이 파일 — 오케스트레이션 헌법
├── README.md              # 프로젝트 소개·사용법
├── INDEX.md               # 전체 산출물 인덱스
├── SETUP.md               # 환경 설치 (Python·apt·폰트·환경변수)
├── agents/                # 활성/레거시 에이전트 계약서
│   ├── _registry.md
│   ├── intake-analyst.md
│   ├── textbook-extractor.md
│   ├── content-curator.md
│   ├── draft-board-builder.md
│   ├── ima2-stylizer.md
│   └── dispatcher.md
├── prompts/               # phase 사양
│   ├── _index.md
│   └── phase{0..5}_*.md
├── tasks/                 # 실행 이력 (감사용)
│   └── {YYYY-MM-DD-slug}/
│       ├── phase0~5/
│       └── DELIVERED.md
├── plans/                 # 살아있는 문서
│   └── roadmap.md
├── research/              # 리서치 보고서
│   └── notebook-generation-from-textbook-research.md
├── examples/              # 참고 예시
│   └── social-5-1-unit1.html
└── INBOX/
    └── README.md
```

## 자율 진행 방침

- 사용자가 "쭉 진행해" 지시한 상태가 기본
- phase0~5 전부 자동 진행이 기본
- 스타일 레퍼런스 누락, 차시 경계 모호, PDF 품질 이상일 때만 사용자 확인
- 파일 생성·수정(note 내부) 자유. ideation 외부 폴더는 **OneDrive 배송 경로만** 쓰기 허용

## 상위 컨텍스트

- 이 프로젝트는 `ideation/`에서 출발했음. 의사결정 이력·이전 실험 산출물은 ideation 기록 참조
- ideation의 dispatcher가 새 요청을 보낼 때 `note/INBOX/`로 들어옴 (`INBOX/README.md` 참조)

## 메모리 참조

사용자 방침은 ideation의 메모리 시스템 (`/home/coseung2/.claude/projects/-mnt-c-Users-----Desktop-Obsidian-Vault-ideation/memory/MEMORY.md`)에 저장됨. 주요 항목:
- `feedback_notebook_style.md` — 학생 필기 스타일 원칙
- `project_baseline_device.md` — 갤탭 S6 Lite 기준 (태블릿 열람 시)
- `feedback_quality_over_devcost.md` — 품질 우선
- 과거의 `feedback_no_ai_doodles.md`는 v1 실제 이미지 소싱 파이프라인 기준이며, 현재 v2 ima2 스타일 변환 파이프라인에는 직접 적용하지 않는다
