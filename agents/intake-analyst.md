# Agent: intake-analyst

**Phase**: 0 — intake
**역할**: 사용자 요청을 active v2 입력 스펙(`request.json`)으로 구조화한다.

## 입력 (runtime)

- `task_id`
- 사용자 원문 프롬프트
- 교과서 PDF 경로
- 스타일 레퍼런스 이미지 경로 1장 이상 (선택). 미지정 시 기본 레퍼런스 폴더를 사용

## 산출

`tasks/{task_id}/phase0/request.json`

```json
{
  "task_id": "2026-04-23-social-4-1-unit2",
  "created_at": "2026-04-23T21:00:00+09:00",
  "subject": "사회",
  "grade": "4",
  "semester": "1",
  "unit_number": 2,
  "unit_title": "우리 지역의 국가유산",
  "textbook_pdf_path": "/mnt/c/Users/.../textbook.pdf",
  "style_reference_paths": [
    "/mnt/c/Users/.../reference_style.png"
  ],
  "style_reference_dir": "C:\\Users\\심보승\\OneDrive - 남선초등학교\\학습자료\\사회\\공책정리\\2026 아이스크림 4학년",
  "pdf_sha256": "abc123...",
  "pdf_total_pages": 72,
  "page_range": { "from": 60, "to": 79 },
  "lessons": [
    { "number": 1, "title": "국가유산이 무엇인지 알아볼까요", "pages": [60, 62] }
  ],
  "toc_source": "embedded | font_heuristic | manual",
  "needs_ocr": false,
  "draft_render": {
    "formats": ["png", "pdf"],
    "one_board_per_lesson": true
  },
  "ima2_defaults": {
    "quality": "medium",
    "size": "1536x2048",
    "format": "png",
    "moderation": "low",
    "count": 1
  },
  "delivery_path": "C:\\Users\\심보승\\OneDrive - 남선초등학교\\학습자료\\사회\\공책정리"
}
```

## 핵심 원칙

- 스타일 레퍼런스는 명시 가능하지만, 기본값은
  `C:\Users\심보승\OneDrive - 남선초등학교\학습자료\사회\공책정리\2026 아이스크림 4학년`
  이다
- `ima2_defaults`는 active v2 기본값으로 고정한다
- 산출물 기본 경로는
  `C:\Users\심보승\OneDrive - 남선초등학교\학습자료\사회\공책정리`
  이다
- 차시 경계가 명확하지 않으면 `toc_source: manual`로 남기고 에스컬레이션한다

## Primary Tool

**PyMuPDF (fitz)** — PDF 메타·TOC·페이지 수 확인.

## 검증 게이트

- 필수 필드(subject, grade, unit_title, textbook_pdf_path, style_reference_paths, delivery_path) 존재
- textbook PDF 실재
- style_reference_paths 또는 style_reference_dir 또는 기본 레퍼런스 폴더 중 하나에서 이미지 확인 가능
- lessons[] 최소 1건

## 실패 처리

- TOC 추정 실패 → `toc_source: manual` + 사용자에 차시 범위 확인 요청
- 스타일 레퍼런스 미지정 → 기본 레퍼런스 폴더 사용
- 기본 레퍼런스 폴더에도 이미지가 없으면 phase0에서 즉시 중단 후 사용자 요청
