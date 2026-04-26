# Notebook Workflow — Active V2 에이전트 레지스트리

교과서 PDF → 학생 공책정리 PNG/PDF 파이프라인의 **활성(v2)** phase별 에이전트 카탈로그.

오케스트레이터(메인 세션)는 직접 편집·렌더·스타일 변환을 하지 않고, 각 phase를 전담 에이전트에 위임한다.

## Phase ↔ 에이전트 매핑

| Phase | 이름 | 에이전트 | 산출 | 검증 게이트 |
|---|---|---|---|---|
| 0 | intake | **intake-analyst** | `phase0/request.json` | 필수 필드 완비 + 스타일 레퍼런스 경로 존재 |
| 1 | extract | **textbook-extractor** | `phase1/text_all_pages.txt`, `phase1/lesson_{NN}.txt`, `phase1/extract.json` | 차시별 텍스트 청크 수 == lessons[] |
| 2 | lesson-spec | **content-curator** | `phase2/notebook.json`, `phase2/notebook_{NN}.json` | 모든 차시에 요약 블록 + 이미지 프레임 설명 존재 |
| 3 | draft-board | **draft-board-builder** | `phase3/lesson_{NN}.png`, `phase3/lesson_{NN}.pdf`, `phase3/board_manifest.json` | 차시별 드래프트 보드 렌더 성공 |
| 4 | stylize | **ima2-stylizer** | `phase4/lesson_{NN}.png`, `phase4/requests.json`, `phase4/prompts/*` | 차시별 최종 PNG 생성 성공 |
| 5 | deliver | **dispatcher** | OneDrive 배송 완료 | 복사본 존재 + sha256 기록 |

## 에이전트 공통 원칙

- **입력 계약 엄수**: 지정된 phase의 산출 파일만 입력으로 사용
- **산출 계약 엄수**: 지정된 경로·스키마대로 저장
- **무인 기본 흐름**: 사용자 검수는 기본 단계가 아니다
- **텍스트 정확도 보존**: phase4는 스타일 변환 단계이지 내용 재작성 단계가 아니다
- **스타일 레퍼런스 우선**: `ima2` 실행 시 첫 번째 레퍼런스는 스타일 앵커, 두 번째는 phase3 draft-board를 사용
- **실패 시 3회 재시도**: 오케스트레이터가 판단

## 호출 포맷

```text
Agent({
  description: "Phase {N} — {agent-name}",
  subagent_type: "general-purpose",
  prompt: "<agents/{agent-name}.md 전문>\n\n---\n런타임 입력:\n- task_id: {yyyy-mm-dd-slug}\n- 입력 파일: {prev_phase_output}\n- 추가 맥락: {optional}"
})
```

## 오케스트레이터가 직접 하는 일

- `tasks/{task_id}/phase{N}/` 폴더 생성
- phase 간 파일 경로 전달
- 검증 게이트 판정
- 재시도·에스컬레이션 결정
- 사용자 커뮤니케이션 (스타일 레퍼런스 누락, PDF 차시 경계 애매함 등)

## 오케스트레이터가 하지 않는 일

- 직접 PDF 파싱
- 직접 구조화 JSON 작성
- 직접 드래프트보드 렌더
- 직접 `ima2` 프롬프트 타이핑/수정
- 에이전트 산출물 수동 수정

## Legacy(v1) 에이전트

다음 문서는 기존 HTML/CSS + 교사 수동 검수 기반 흐름 기록용이다.

- `image-scout.md`
- `reviewer.md`
- `html-builder.md`
- `pdf-renderer.md`

active pipeline의 기준 문서는 아니다.
