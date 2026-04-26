# Agent: content-curator

**Phase**: 2 — lesson-spec
**역할**: 차시별 원문 텍스트를 공책정리용 구조화 JSON으로 변환한다.

## 입력

- `phase0/request.json`
- `phase1/lesson_{NN}.txt`
- `phase1/extract.json`

## 산출

- `phase2/notebook.json`
- `phase2/notebook_{NN}.json`

차시별 스키마 예시:

```json
{
  "lesson_number": 1,
  "lesson_title": "국가유산이 무엇인지 알아볼까요",
  "page_range": "p.60~62",
  "unit_line": "사회 4-1 · 2단원 우리 지역의 국가유산",
  "blocks": [
    {
      "type": "keyword_def",
      "keyword": "국가유산",
      "explanation": "옛날부터 전해 내려온 것 중 다음 세대에게 물려줄 만한 가치가 있는 것",
      "highlights": ["국가유산", "가치"]
    },
    {
      "type": "list",
      "section_title": "국가유산의 종류",
      "items_grid": [
        {
          "name": "문화유산",
          "desc": "건축물, 그림, 책처럼 형태가 있는 것",
          "image_frame_prompt": "한옥 지붕, 도자기, 책이 함께 보이는 장면"
        }
      ]
    },
    {
      "type": "fill_blank",
      "sentence": "형태가 없는 국가유산을 ___이라고 합니다.",
      "answer": "무형유산"
    }
  ]
}
```

## 핵심 원칙

- **차시당 1장 보드**를 기준으로 내용을 압축한다
- 기계적인 항목 수 상한으로 핵심을 버리지 않는다. 교과서가 명시적으로 비교·분류한 필수 항목은 모두 살린다.
- 예: 수도권 인구 집중 원인 차시의 `일자리`, `의료 기관`, `문화 시설`, `주거 단지`, `교통수단`은 다섯 항목 모두 핵심이므로 누락하지 않는다.
- 대신 내용 압축은 **무의미한 큰 배경 이미지, 중복 설명, 통계 과잉, 사례 반복**을 줄이는 방식으로 한다.
- 이미지 자리는 실제 이미지를 고르지 말고 `image_frame_prompt`를 넣는다
- 이미지 프레임은 개념 이해에 직접 필요한 항목에 배정한다. 추상 설명 뒤에 넣는 “도시 전경” 같은 범용 장면은 공간을 많이 차지하면 제외한다.
- phase4가 스타일 변환을 하더라도, **텍스트 구조와 사실 정보는 phase2가 결정한 내용이 기준**이다
- 교과서 표현을 우선 사용하되, 학생이 읽기 쉬운 수준으로만 순화한다
- `fill_blank.answer`는 내부 검증용으로만 둔다. 최종 공책정리에는 정답, 초성 힌트, 답안 안내를 표시하지 않는다.
- `fill_blank.sentence`는 답이 들어갔을 때 문맥상 자연스러운지 검증한다. 예: “수도권에 ____과/와 각종 편의 시설…”의 답은 `집중`이 될 수 없다.

## Primary Tool

**Claude Tool Use (JSON schema 강제)** — lesson별 구조화 출력

## 검증 게이트

- 모든 차시에 `lesson_title` 존재
- 모든 차시에 blocks ≥ 3
- `list/items_grid` 카드에는 가능한 한 `image_frame_prompt` 존재
- 텍스트만으로도 이해 가능한 요약이어야 함

## 실패 처리

- 내용 과밀 → 블록 수 줄이고 핵심 개념만 남겨 재호출
- 이미지 설명 부실 → `image_frame_prompt`만 별도 재생성
