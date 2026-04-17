# Notebook Workflow — 에이전트 레지스트리

교과서 PDF → 학생 공책정리 PDF 파이프라인의 각 phase를 담당하는 서브에이전트 카탈로그.

오케스트레이터(메인 세션)는 직접 리서치·편집을 하지 않고 `Agent` 도구로 각 에이전트를 호출한다.

## Phase ↔ 에이전트 매핑

| Phase | 이름 | 에이전트 | 산출 | 검증 게이트 |
|---|---|---|---|---|
| 0 | intake | **intake-analyst** | `phase0/request.json` | 필수 필드 완비 |
| 1 | extract | **textbook-extractor** | `phase1/text.txt`, `phase1/images/`, `phase1/image_manifest.json` | 이미지 추출 수 > 0 |
| 2 | draft | **content-curator** | `phase2/notebook_draft.md`, `phase2/image_candidates.json` | 모든 페이지에 블록 ≥ 3 |
| 3 | validate | **(교사 수동)** — 에이전트 없음 | `phase3/notebook_draft.approved.md` | 파일 존재 + `status: approved` 프론트매터 |
| 4 | image-source | **image-scout** | `phase4/images/`, `phase4/image_map.json` | 사용하기로 한 모든 블록에 이미지 경로 존재 |
| 5 | render | **html-builder** | `phase5/notebook.html` | HTML valid + 이미지 경로 해석됨 |
| 6 | pdf | **pdf-renderer** | `phase6/notebook.pdf` | PDF 페이지 수 == 입력 페이지 수 |
| 7 | deliver | **dispatcher** | OneDrive 배송 완료 | 복사본 파일 존재 |

## 에이전트 공통 원칙

- **입력 계약 엄수**: 지정된 phase의 산출 파일만 입력. 다른 phase 결과 읽지 않음
- **산출 계약 엄수**: 지정된 경로·스키마대로만 저장
- **ambiguity 유보**: 판단 불가 시 `_questions.md`에 적어 오케스트레이터에 에스컬레이션
- **저작권 원칙**: 교과서 삽화는 학교 교육 목적 이용 한정. 외부 이미지는 CC/공공 우선 + 출처 메타데이터 필수
- **실패 시 3회 재시도**: 오케스트레이터가 판단

## 호출 포맷

```
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
- 사용자 커뮤니케이션 (draft 검증 요청, 이미지 선택 요청 등)

## 오케스트레이터가 하지 않는 일

- 직접 pdftotext·pdfimages 실행 (extractor 담당)
- 직접 이미지 서치 (scout 담당)
- 직접 HTML 편집 (builder 담당)
- 에이전트 산출물 수정 (재호출로 해결)
