# Notebook Workflow — 파이프라인 실행 순서

## 흐름

```
[0] intake ──→ [1] extract ──→ [2] draft ──→ ⏸ [3] validate (교사) ──→
    [4] image-source ──→ [5] render ──→ [6] pdf ──→ [7] deliver
```

⏸ = 에이전트 실행 일시 정지. 교사가 파일 편집 후 재개.

## Phase별 사양

| # | 파일 | 담당 |
|---|---|---|
| 0 | [phase0_intake.md](phase0_intake.md) | intake-analyst |
| 1 | [phase1_extract.md](phase1_extract.md) | textbook-extractor |
| 2 | [phase2_draft.md](phase2_draft.md) | content-curator |
| 3 | [phase3_validation.md](phase3_validation.md) | **교사 수동** (에이전트 없음) |
| 4 | [phase4_image_source.md](phase4_image_source.md) | image-scout |
| 5 | [phase5_render.md](phase5_render.md) | html-builder |
| 6 | [phase6_pdf.md](phase6_pdf.md) | pdf-renderer |
| 7 | [phase7_deliver.md](phase7_deliver.md) | dispatcher |

## 검증 게이트 요약

각 phase 완료 시 오케스트레이터가 게이트 통과 여부 판정. 실패 시 최대 3회 재호출.

| 게이트 | 위치 | 통과 조건 |
|---|---|---|
| 입력완비 | phase0 직후 | request.json 필수 필드 + PDF 실재 |
| 추출성공 | phase1 직후 | text ≥ 1 byte + images 디렉토리 비어있지 않음 |
| 드래프트완성 | phase2 직후 | 모든 페이지에 블록 ≥ 3 + 이미지 후보 ≥ 1 |
| **교사승인** | phase3 직후 | `status: approved` + 파일 변경 타임스탬프 갱신 |
| 이미지확정 | phase4 직후 | image_map.json의 모든 경로가 실재 파일 |
| 렌더성공 | phase5 직후 | HTML valid + 이미지 해석 |
| PDF완성 | phase6 직후 | PDF 페이지 수 일치 |
| 배송완료 | phase7 직후 | OneDrive 복사본 존재 |

## 스킵 규칙

- 교과서 삽화가 전혀 없는 단원: phase1의 `image_manifest.empty=true` 플래그 → phase4에서 외부 서치 비중 ↑
- 페이지 1쪽짜리 미니 정리: phase0에서 `target_pages_in_notebook=1` 지정 → phase2부터 1페이지로 축소

## Task 폴더 구조

```
tasks/{YYYY-MM-DD-slug}/
├── phase0/request.json
├── phase1/
│   ├── text.txt
│   ├── text_by_page/
│   ├── images/
│   └── image_manifest.json
├── phase2/
│   ├── notebook_draft.md
│   └── image_candidates.json
├── phase3/
│   └── notebook_draft.approved.md    ← 교사가 저장
├── phase4/
│   ├── images/
│   ├── image_map.json
│   └── attribution.md
├── phase5/
│   └── notebook.html
├── phase6/
│   └── notebook.pdf
└── DELIVERED.md
```
