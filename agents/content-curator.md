# Agent: content-curator

**Phase**: 2 — draft
**역할**: 교과서 원문 + 삽화 카탈로그 → 교사 검토용 `notebook_draft.md` 생성.

## 입력

- `phase0/request.json`
- `phase1/extract.json` 또는 `phase1/text_by_page/*.txt`
- `phase1/image_manifest.json`

## 산출

- `phase2/notebook_draft.md` (프론트매터 `status: draft`)
- `phase2/notebook.json` (구조화 원본, 검증·재생성용)
- `phase2/image_candidates.json`

## Primary Tool

**Anthropic Tool Use (JSON schema 강제)** — 스키마 위반 시 모델이 자체 재시도, 단일 의존성.

```bash
pip install anthropic jsonschema
```

## 핵심 코드 — Tool Use 스키마

```python
import anthropic, json, jsonschema

TOOL = {
  "name": "emit_notebook",
  "description": "교과서 차시를 학생 공책정리용 JSON으로 변환",
  "input_schema": {
    "type": "object",
    "required": ["lesson_title", "page_range", "blocks"],
    "properties": {
      "lesson_title": {"type": "string", "maxLength": 40},
      "page_range": {"type": "string"},
      // learning_goals 필드 제거됨 (2026-04-15 교사 피드백: 학습목표는 교사용 문구, 학생 공책에 불필요)
      "blocks": {
        "type": "array", "minItems": 3, "maxItems": 6,
        "items": {
          "type": "object",
          "required": ["type", "checkbox"],
          "properties": {
            "type": {"enum": ["keyword_def", "list", "callout", "bubble", "fill_blank"]},
            "keyword": {"type": "string", "maxLength": 20},
            "explanation": {"type": "string", "maxLength": 120},
            "items": {"type": "array", "items": {"type": "string"}},
            "text": {"type": "string"},
            "speaker": {"type": "string"},
            "sentence": {"type": "string"},
            "answer": {"type": "string"},
            "image_candidate_ids": {"type": "array", "items": {"type": "string"}},
            "image_search_query": {"type": "string"},
            "checkbox": {"type": "boolean", "const": true}
          }
        }
      },
      "excluded_candidates": {
        "type": "array",
        "items": {"type": "object", "required": ["keyword", "reason"],
                  "properties": {"keyword": {"type": "string"},
                                 "reason": {"type": "string"}}}
      }
    }
  }
}

SYSTEM = """너는 초등 공책정리 도우미다.
원칙:
- 키워드는 교과서 본문에서 추출한 어휘만 사용. AI 창작 금지.
- 페이지당 블록 3~6개. 과도 밀도 지양.
- 설명은 한 문장, 초등 어휘만.
- "fill_blank"의 sentence는 교과서의 '한 문장 정리' 원문 우선.
- 이미지 후보는 phase1 image_manifest.images[].id 로 지정.
  적합한 교과서 삽화가 없으면 image_search_query 필드에 영어 학술명 쿼리 제공.
- 교사가 뺀 것도 볼 수 있게 excluded_candidates에 이유와 함께 기록."""

client = anthropic.Anthropic()
resp = client.messages.create(
    model="claude-sonnet-4-5", max_tokens=4000,
    tools=[TOOL], tool_choice={"type": "tool", "name": "emit_notebook"},
    system=SYSTEM,
    messages=[{"role": "user", "content": user_prompt_with_raw_text}]
)
note = resp.content[0].input
jsonschema.validate(note, TOOL["input_schema"])
```

## 마크다운 변환

```python
def to_md(note):
    md = f"---\ntask_id: {task_id}\nstatus: draft\n---\n\n"
    md += f"## 📄 {note['lesson_title']} (교과서 {note['page_range']})\n\n"
    # 학습 목표 섹션 제거 (2026-04-15 교사 피드백)
    md += "### 🔑 키워드:설명\n"
    for b in note["blocks"]:
        if b["type"] == "keyword_def":
            md += f"- [x] **{b['keyword']}** : {b['explanation']}\n"
    md += "\n### 📌 Callout\n"
    for b in note["blocks"]:
        if b["type"] == "callout":
            md += f"- [x] {b['text']}\n"
    md += "\n### 💬 말풍선\n"
    for b in note["blocks"]:
        if b["type"] == "bubble":
            md += f"- [x] {b.get('speaker','')}: \"{b['text']}\"\n"
    md += "\n### 🖼 이미지 후보\n"
    for b in note["blocks"]:
        if b.get("image_candidate_ids"):
            for iid in b["image_candidate_ids"]:
                md += f"- [ ] `{iid}` — 교과서 삽화\n"
        if b.get("image_search_query"):
            md += f"- [ ] `external:search:{b['image_search_query']}` — 외부 CC 서치\n"
    # fill_blank
    for b in note["blocks"]:
        if b["type"] == "fill_blank":
            md += f"\n### 📝 한 문장 정리\n- {b['sentence']} (정답: {b['answer']})\n"
    md += "\n---\n\n## 🗑 LLM이 뺐지만 교사가 복구 가능한 후보\n"
    for ex in note.get("excluded_candidates", []):
        md += f"- **{ex['keyword']}** — (이유: {ex['reason']})\n"
    md += "\n## 📝 교사 추가 지시\n> 여기에 쓰세요.\n"
    return md
```

## Fallback

- **Instructor + Pydantic**: OpenAI·Gemini 병행 시. 단일 Claude 환경엔 과투자
- **Guided JSON (llama.cpp)**: 로컬 추론. 한글 품질 낮아 교과서 맥락엔 비추
- 블록 수 미달 시 차시 원문 ±1 차시 병합 후 재호출

## 선별 원칙

1. 키워드는 교과서 본문 어휘만
2. 페이지당 블록 3~6개
3. fill_blank는 교과서 원문 복제
4. 이미지 후보는 교과서 삽화 우선, 없을 때만 `image_search_query`
5. 🗑 섹션에 뺀 이유 기록 — 투명성
6. **무관한 이미지 억지 삽입 금지** (2026-04-17): `image_candidate_ids`에 블록의 keyword/explanation 개념과 무관한 이미지를 넣지 말 것. 적합한 교과서 삽화가 없으면 **빈 배열 `[]`로 두는 것이 낫다**. 예: "기후 특징" 블록에 홍수 사진, "꽃샘추위" 블록에 서리 사진 — 이런 '대충 비슷해 보이는' 매핑 금지. 텍스트 정의만으로 충분한 블록이 많다.

## 흐름(flow) 다이어그램 (`keyword_def` 보조 필드)

키워드가 **순차적 흐름**(강의 발원→중류→하구, 시대 변천, 식물 성장 단계 등)을 가질 때, `flow` 배열로 시각화한다 (2026-04-15 교사 피드백 — 한강: 검룡소→두물머리→서울→황해).

- 스키마 확장: `keyword_def` 블록에 `flow` 추가
  ```json
  "flow": [
    {"name": "검룡소", "subtitle": "발원지", "image": "p006_5", "desc": "강원 태백시"},
    {"name": "두물머리", "subtitle": "남한강+북한강 합류", "image": "p006_3", "desc": "경기 양평군"},
    {"name": "서울", "subtitle": "수도권 관통", "image": null, "desc": "서울특별시"},
    {"name": "황해", "subtitle": "바다로 흘러감", "image": null, "desc": "하구"}
  ]
  ```
- 단계별 교과서 사진이 있으면 `image`에 ID, 없으면 `null` (렌더에서 이모지 폴백)
- 단계 수 3~6 권장. 단계가 1~2개면 일반 키워드 설명만으로 충분

## 카테고리 그리드 (`list` 블록 + 1:1 이미지)

`list` 블록이 **분류 항목 N개**(예: 지형 6가지, 사회 4계급, 식물 부위 5개)를 다룰 때, 각 항목별 대표 이미지가 교과서에 1:1로 존재하면 **그리드 형태**로 구조화한다 (2026-04-15 교사 피드백).

- 스키마 확장: `items` 대신 `items_grid` 사용
  ```json
  "items_grid": [
    {"name": "산지", "desc": "높고 낮은 산이 모여 있는 곳", "image": "p006_2", "loc": "북한산"}
  ]
  ```
- 각 `image`는 phase1 이미지 ID, `loc`는 교과서에 표기된 구체 장소·예시명
- 이미지 1:1 매칭이 불가능하면(N개 중 일부만 존재) 일반 `items` 배열로 폴백
- 렌더 단계(phase5)는 이 구조를 받아 3열 그리드 카드(이미지+이름+설명+위치) 출력
- `grid_cols`: 항목 수에 맞춰 열 수 조정 필요 시 명시 (기본 3열, 4항목=2, 6항목=3, 9항목=3). 2×2 배치는 `grid_cols: 2`

## section_title과 keyword 중복 시 section_title 삭제 (2026-04-17)

`keyword_def` 블록에서 `section_title`이 `keyword`와 동일하거나, keyword를 그대로 반복하는 내용이면 `section_title`을 **넣지 않는다**. section_title은 keyword에 없는 부가 맥락(질문형, 대조, 범위 등)을 제공할 때만 의미가 있다.

- 잘못된 예: `"keyword": "계절풍"`, `"section_title": "계절풍"` -- 동어 반복
- 잘못된 예: `"keyword": "자연재해"`, `"section_title": "자연재해란?"` -- keyword를 그대로 반복
- 올바른 예: `"keyword": "계절풍"`, `"section_title": "여름·겨울 바람이 이렇게 다르다"` -- 부가 맥락 제공
- section_title 없는 블록은 keyword 형광펜만 출력되며 충분히 가독성 있다.

## 초등학생 어휘 규칙 — 어려운 한자어 금지 (2026-04-17)

설명(`explanation`, `desc`, `sentence` 등)에 초등학생이 어려워하는 한자어를 쓰지 않는다. 쉬운 우리말로 바꾼다.

| 금지 어휘 | 대체 |
|---|---|
| 추세 | 흐름 |
| 경향 | 흐름 |
| 추이 | 변화 |
| 양상 | 모습 |
| 현저한 | 눈에 띄는 |
| 급증 | 크게 늘어남 |
| 급감 | 크게 줄어듦 |

이 목록은 예시이며, 초등 5학년 교과서에 등장하지 않는 한자어는 전부 교체 대상이다.

## sub_kv 지원 — keyword_def 하위 키워드 (2026-04-17)

`keyword_def` 블록 안에 `sub_kv` 배열을 넣어 하위 키워드를 추가할 수 있다. 상위 keyword의 세부 분류·구성 요소를 나열할 때 사용.

```json
{
  "type": "keyword_def",
  "keyword": "지구온난화",
  "explanation": "화석 연료 소비가 늘고 온실가스 많이 배출 → 지구의 기온이 높아짐",
  "sub_kv": [
    {"keyword": "온실가스", "explanation": "이산화 탄소, 메탄 등 온실 효과를 일으키는 가스"}
  ]
}
```

- sub_kv 내 각 항목은 `keyword` + `explanation` 필수
- 렌더러(html-builder)가 상위 kv 아래에 들여쓰기로 출력
- sub_kv가 3개 이상이면 별도 블록으로 분리 권장

## section_title 선행 기호 금지 (2026-04-17)

`section_title` 필드에 `◆ ◇ ✦ ▶ ※ ★ ☆ ● ○ ◎` 등 선행 기호를 **절대 넣지 말 것**. 이런 기호는 렌더러(html-builder)가 CSS 클래스(`.diamond`, `.gem`, `.star`, `.bullet` 등)의 `::before`로 자동 삽입한다. JSON 텍스트에 기호를 같이 넣으면 `◆ ◆`처럼 **동일 기호 2연속**으로 찍혀서 feedback_no_double_asterisk 규칙을 위반한다.

- 올바른 예: `"section_title": "여름 vs 겨울, 얼마나 다를까?"` + 별도로 `"color": "blue"` (CSS class 제어)
- 잘못된 예: `"section_title": "◆ 여름 vs 겨울, 얼마나 다를까?"` ← 렌더에서 `◆ ◆`로 찍힘
- 색·기호 선택은 렌더러의 몫. curator는 텍스트만 생성.

## 제외 콘텐츠 (학생 공책 = 핵심 정리. 교사용 문구·도입부 금지)

- **학습 목표 생성 금지** (2026-04-15 교사 피드백): "○○을 설명할 수 있어요" 류는 교사용 문구. 학생 공책에 넣지 않는다. `learning_goals` 필드는 빈 배열로 둔다 (스키마가 요구하면 `[""]` 대신 스키마 수정 고려).
- **도입 bubble 금지** (2026-04-15 교사 피드백): "한강은 어디까지 이어져 있을까? 여행을 떠나 볼까?" 류 수업 도입 이야기·동기유발·감정 표현 bubble 제외. bubble은 **개념 보조 설명 용도**로만 쓰되(예: "갯벌은 바다 식물이 많이 살아."), 도입·호기심 유발 멘트는 배제.
- 교실 놀이·활동 안내(예: "빙고 놀이 해 봅시다") 제외 — 활동은 교사가 직접 안내

이 원칙들은 `input_schema` 생성 단계에서 강제: bubble 생성 시 도입성 여부 self-check, learning_goals 생성하지 않음.

## 허용 도구

`Read`, `Write`, `Bash`(Python + anthropic SDK), `Grep`

## 검증 게이트

- `jsonschema.validate(note, TOOL.input_schema)` 통과
- 모든 차시 블록 ≥ 3
- 이미지 후보 or 검색 쿼리 ≥ 1 (차시당)
- 🗑 섹션·교사 지시 섹션 포함
- 프론트매터 `status: draft`

## 실패 처리

- 키워드 중복 (`set` 길이 불일치) → 재생성
- 학습목표 동어반복 → 시스템 프롬프트에 "직전 생성과 다른 표현" 추가 후 재시도
- 원문 너무 짧음 → `_questions.md` 기록 + 차시 범위 재검토 요청

## 참고

- https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- https://json-schema.org/learn/miscellaneous-examples
