# AGENTS.md

이 문서는 **Codex가 작업 시작 전에 먼저 확인하는 거버넌스/헌법 문서**다.

## 원본 정책

- 이 저장소의 실제 정책 원본은 [`CLAUDE.md`](CLAUDE.md)다.
- Codex는 작업을 시작할 때 **항상 `CLAUDE.md`를 먼저 읽고**, 이 문서는 그 진입점으로 사용한다.
- 정책 수정은 **`CLAUDE.md` 우선**으로 반영하고, 이 파일은 그 변경을 따라간다.

## Codex 작업 규칙

1. 작업 시작 전 `CLAUDE.md`를 읽는다.
2. 활성 파이프라인은 `CLAUDE.md`, `prompts/_index.md`, `agents/_registry.md` 기준으로 해석한다.
3. legacy(v1) 문서보다 active(v2) 문서를 우선한다.
4. 중간 사용자 검수는 기본 단계가 아니다. 품질 이상, 차시 경계 모호, 스타일 레퍼런스 누락일 때만 사용자 확인으로 에스컬레이션한다.
5. phase4 스타일 변환은 `ima2` 기준으로 수행하고, phase2/3의 텍스트 정확도를 훼손하지 않는다.

## 현재 활성 파이프라인 요약

```text
[0] intake
→ [1] extract
→ [2] lesson-spec
→ [3] draft-board
→ [4] stylize (ima2)
→ [5] deliver
```

## 활성 문서

- 거버넌스 원본: `CLAUDE.md`
- phase 인덱스: `prompts/_index.md`
- 에이전트 레지스트리: `agents/_registry.md`
- 실행 로드맵: `plans/roadmap.md`

## 메모

- `CLAUDE.md`와 이 파일이 충돌하면 `CLAUDE.md`를 우선한다.
- 이 파일의 목적은 “Codex가 먼저 읽는 입구 문서”를 명시하는 것이다.
