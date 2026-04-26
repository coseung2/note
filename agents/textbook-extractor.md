# Agent: textbook-extractor

**Phase**: 1 — extract
**역할**: 교과서 PDF에서 전체 텍스트를 추출하고, 차시별 텍스트 청크를 잘라 phase2에 전달한다.

## 입력

`tasks/{task_id}/phase0/request.json`

## 산출

```text
tasks/{task_id}/phase1/
├── text_all_pages.txt
├── lesson_01.txt
├── lesson_02.txt
└── extract.json
```

`extract.json` 예시:

```json
{
  "task_id": "2026-04-23-social-4-1-unit2",
  "page_range": { "from": 60, "to": 79 },
  "lessons": [
    {
      "lesson_number": 1,
      "lesson_title": "국가유산이 무엇인지 알아볼까요",
      "pages": [60, 62],
      "text_file": "lesson_01.txt"
    }
  ]
}
```

## 핵심 원칙

- active v2에서는 **이미지 추출이 핵심이 아니다**
- phase1의 목적은 차시명과 차시별 본문 텍스트를 안정적으로 자르는 것이다
- 표/그림 캡션이 본문과 섞여도 괜찮지만, 차시 범위를 잘못 자르면 안 된다

## Primary Tool

**PyMuPDF (fitz)** — PDF 텍스트 추출, 페이지 범위 분할

## 검증 게이트

- `text_all_pages.txt` 비어있지 않음
- `lesson_{NN}.txt` 개수 == request.json의 lessons[] 길이
- 각 lesson 파일은 지정된 page range 안의 텍스트만 포함

## 실패 처리

- 스캔본으로 텍스트 추출 실패 → `needs_ocr=true`를 유지하고 OCR fallback 실행
- 차시 경계 혼선 → `_questions.md` 작성 후 사용자 확인
