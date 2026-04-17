# note — 산출물 인덱스

## 📁 구조

```
note/
├── CLAUDE.md              # 오케스트레이션 헌법
├── README.md              # 프로젝트 소개·빠른 시작
├── INDEX.md               # 이 파일
├── SETUP.md               # 환경 설치
├── template.html          # 재사용 HTML/CSS 스켈레톤
│
├── agents/                # 에이전트 계약서 (8건)
│   ├── _registry.md
│   ├── intake-analyst.md
│   ├── textbook-extractor.md
│   ├── content-curator.md
│   ├── image-scout.md
│   ├── html-builder.md
│   ├── pdf-renderer.md
│   └── dispatcher.md
│
├── prompts/               # phase 사양 (8건 + 인덱스)
│   ├── _index.md
│   └── phase{0..7}_*.md
│
├── tasks/                 # 실행 이력
│   └── {YYYY-MM-DD-slug}/phase{0..7}/
│
├── plans/
│   └── roadmap.md         # v1~v6 로드맵·의사결정 이력
│
├── research/
│   └── notebook-generation-from-textbook-research.md
│
├── examples/
│   └── social-5-1-unit1.html  # v1 수동 작성 샘플
│
└── INBOX/                 # ideation dispatcher가 보내는 요청
    └── README.md
```

## 🧭 읽는 순서

처음 진입 시:
1. **`README.md`** — 프로젝트 한 페이지 요약
2. **`CLAUDE.md`** — 오케스트레이션 원칙
3. **`SETUP.md`** — 환경 설치
4. **`prompts/_index.md`** — 파이프라인 실행 순서

새 작업 시작 시:
- Claude Code에 자연어로 요청 → 자동 phase0 시작
- 또는 수동으로: `tasks/{새task_id}/phase0/request.json` 직접 작성

워크플로우 개선 시:
- 특정 phase 문제 → `agents/{해당-에이전트}.md` 계약서 수정
- 전체 흐름 변경 → `prompts/_index.md` + `CLAUDE.md`

## 🔗 외부 참조

- 의사결정 이력·이전 실험: `../ideation/` (참조 전용)
- OneDrive 배송 위치: `OneDrive - 남선초등학교\학습자료\{과목}\공책정리\`
- 사용자 메모리: `~/.claude/projects/.../memory/MEMORY.md`

## 📜 로그

- 2026-04-15: ideation/notebook-workflow에서 이식. 프로젝트 폴더 정식 분리.
