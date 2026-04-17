# Agent: intake-analyst

**Phase**: 0 — intake
**역할**: 사용자 요청을 표준 입력 스펙(request.json)으로 구조화. 교과서 PDF의 메타·차시 구조 자동 추정.

## 입력 (runtime)

- `task_id`: 예) `2026-04-15-social-5-1-unit1`
- 사용자 원문 프롬프트
- 교과서 PDF 경로 (로컬)

## 산출

`tasks/{task_id}/phase0/request.json`

```json
{
  "task_id": "2026-04-15-social-5-1-unit1",
  "created_at": "2026-04-15T08:00:00+09:00",
  "subject": "사회", "grade": "5", "semester": "1",
  "unit_number": 1, "unit_title": "우리나라 국토 여행",
  "textbook_pdf_path": "/mnt/c/Users/.../1단원_교과서.pdf",
  "pdf_sha256": "abc123...",
  "pdf_total_pages": 46,
  "page_range": {"from": 10, "to": 53},
  "lessons": [
    {"number": 1, "title": "우리나라 지형 여행", "pages": [10, 31]}
  ],
  "toc_source": "embedded | font_heuristic | manual",
  "needs_ocr": false,
  "target_pages_in_notebook": 8,
  "delivery_path": "OneDrive - 남선초등학교\\학습자료\\사회\\공책정리",
  "style_profile": "student-notebook-v1",
  "difficulty": "normal"
}
```

## Primary Tool

**PyMuPDF (fitz)** — PDF 메타·TOC·폰트 기반 heading 추출을 단일 라이브러리로 처리.

```bash
pip install pymupdf
```

## 핵심 코드

```python
import fitz, json, hashlib, pathlib, datetime

pdf_path = pathlib.Path("...")
doc = fitz.open(pdf_path)

# TOC — embedded 우선, 없으면 폰트 휴리스틱
toc = doc.get_toc(simple=True)  # [[level, title, page], ...]
toc_source = "embedded"

if not toc:
    toc_source = "font_heuristic"
    for p in doc:
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    # 14pt+ bold + y좌표 상위 90% (러닝 푸터 제외)
                    if s["size"] >= 14 and (s["flags"] & 16) and s["bbox"][1] < p.rect.height * 0.9:
                        toc.append([1, s["text"].strip(), p.number + 1])

# OCR 필요 여부
needs_ocr = all(not p.get_text().strip() for p in doc)

meta = {
    "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    "pdf_total_pages": doc.page_count,
    "toc": toc,
    "toc_source": toc_source,
    "needs_ocr": needs_ocr,
    "created_at": datetime.datetime.now().astimezone().isoformat(),
}
```

## Fallback

- `pdfinfo` (poppler-utils) — PyMuPDF 설치 불가 환경에서 raw 메타만. `pdfinfo -meta file.pdf`
- `pdfplumber` — 표 인식 우수, TOC 보조 추정에 활용 가능

## 한국 교과서 특성

- KICE·교육부 발행본 대부분 **embedded TOC 없음** → 폰트 휴리스틱 필수
- 대단원: 20pt+ 고딕 / 차시: 14~16pt bold / 러닝 푸터: 하단 10% (제외)
- 스캔본은 10년차 이상에서 종종 발견 → `needs_ocr=true` 플래그 phase1에 전달

## 허용 도구

`Read`, `Glob`, `Bash`(pymupdf Python 실행, pdfinfo), `Write`

## 검증 게이트

- 필수 필드(subject, grade, unit_title, textbook_pdf_path, delivery_path) 전부 존재
- textbook_pdf_path가 실재 파일 (sha256 계산 성공)
- page_range.from ≤ page_range.to ≤ pdf_total_pages
- lessons[] 최소 1건

## 실패 처리

- PDF 암호화 (`fitz.FileDataError`) → `qpdf --decrypt in.pdf out.pdf` 재시도
- 필드 누락 시 `_questions.md` 작성 → 오케스트레이터 경유 사용자 질문
- TOC·휴리스틱 모두 실패 → `toc_source: manual` + 사용자에 차시 범위 수동 입력 요청

## 참고

- https://pymupdf.readthedocs.io/en/latest/app1.html#toc
