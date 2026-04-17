# Phase 0 — intake

**에이전트**: intake-analyst (`agents/intake-analyst.md`)

## 목적
사용자 자유 프롬프트 + 교과서 PDF 경로를 표준 `request.json`으로 구조화.

## 트리거
사용자가 교과서 PDF와 "공책정리 만들어줘"류의 요청을 주었을 때.

## 입력
- 사용자 원문
- 교과서 PDF 경로 (로컬)

## 산출
`tasks/{task_id}/phase0/request.json`

## 검증 게이트
필수 필드(subject, grade, unit_title, textbook_pdf_path, delivery_path) 완비 + PDF 실재.

## 다음 phase
→ phase1 (extract)
