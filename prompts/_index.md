# Notebook Workflow — Active V2 파이프라인 실행 순서

## 흐름

```text
[0] intake
→ [1] extract
→ [2] lesson-spec
→ [3] draft-board
→ [4] stylize (ima2)
→ [5] deliver
```

- 기본은 **무인 자동 실행**
- 중간 사용자 검수 단계는 없다
- 기존 HTML/CSS + image-source + 교사 승인 흐름은 **legacy(v1)** 로 남겨두되, active flow에서는 사용하지 않는다

## Phase별 사양

| # | 파일 | 담당 |
|---|---|---|
| 0 | [phase0_intake.md](phase0_intake.md) | intake-analyst |
| 1 | [phase1_extract.md](phase1_extract.md) | textbook-extractor |
| 2 | [phase2_draft.md](phase2_draft.md) | content-curator |
| 3 | [phase3_draft_board.md](phase3_draft_board.md) | draft-board-builder |
| 4 | [phase4_stylize.md](phase4_stylize.md) | ima2-stylizer |
| 5 | [phase5_deliver.md](phase5_deliver.md) | dispatcher |

## 검증 게이트 요약

| 게이트 | 위치 | 통과 조건 |
|---|---|---|
| 입력완비 | phase0 직후 | request.json 필수 필드 + PDF 실재 + 스타일 레퍼런스 경로 존재 |
| 추출성공 | phase1 직후 | 차시별 텍스트 청크 생성 + lessons[] 수 일치 |
| 스펙완성 | phase2 직후 | 모든 차시에 제목·요약 블록·이미지 프레임 설명 ≥ 1 |
| 드래프트보드완성 | phase3 직후 | 차시별 PNG 생성 + 프레임 내부 설명 노출 |
| 스타일변환성공 | phase4 직후 | 차시별 최종 PNG 존재 + `ima2` 요청 로그 정상 |
| 배송완료 | phase5 직후 | OneDrive 복사본 존재 + sha256 기록 |

## Task 폴더 구조 (active v2)

```text
tasks/{YYYY-MM-DD-slug}/
├── phase0/request.json
├── phase1/
│   ├── text_all_pages.txt
│   ├── lesson_01.txt
│   ├── lesson_02.txt
│   └── extract.json
├── phase2/
│   ├── notebook.json
│   ├── notebook_01.json
│   └── notebook_02.json
├── phase3/
│   ├── lesson_01.html
│   ├── lesson_01.png
│   ├── lesson_01.pdf
│   └── board_manifest.json
├── phase4/
│   ├── lesson_01.png
│   ├── lesson_02.png
│   ├── requests.json
│   └── prompts/
└── phase5/
    ├── manifest.sha256
    └── DELIVERED.md
```

## Legacy 문서

- `phase3_validation.md`
- `phase4_image_source.md`
- `phase5_render.md`
- `phase6_pdf.md`
- `phase7_deliver.md`

위 문서들은 v1 HTML/CSS + 수동 승인 흐름 기록용이며, active pipeline의 실행 기준은 아니다.
