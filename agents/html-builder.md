# Agent: html-builder

**Phase**: 5 — render
**역할**: 승인 draft + 확정 이미지 → `template.html` 주입 → 완성 HTML.

## 공책 스타일 핵심 (2026-04-15 교사 피드백)

학생이 직접 필기한 공책처럼 보여야 한다. 교과서·집필진 요약페이지 톤 금지.

**필수 요소** (레퍼런스: `OneDrive - 남선초등학교\학습자료\사회\공책정리\사회5-1_1단원_공책정리본_v2_HTML실험.pdf`):

1. **줄 공책 배경** — 아이보리 #fffcf0 + 가로 줄(7mm 간격, 연한 파랑) + 왼쪽 빨간 세로 마진선
2. **손글씨 폰트** — `Gaegu`(본문), `Nanum Pen Script`(주석·필기체), `Hi Melody`(메인 제목), `Gaegu 700`(섹션 타이틀). **`Black Han Sans` 사용 금지** (2026-04-15 피드백: 글자선이 너무 굵어 겹쳐 인식 어려움). 시스템 고딕 금지
3. **섹션 구분은 기호만** (2026-04-15 재피드백) — 포스트잇/스티커 박스 배경·테두리 **금지**. 실제 필기처럼 기호(◆ ◇ ✦ ▶ ※)로만 섹션 타이틀 앞에 붙여 구분. 내용 본문은 줄 공책지 위에 바로 써진 듯 배치. 이모지는 🔑🗺📝 등을 아주 제한적으로만 사용
4. **마스킹테이프** — ~~상단 좌우에 기울어진 파스텔 테이프~~ **제거** (2026-04-15 교사 피드백: 불필요). 상단은 제목·페이지ref만
5. **형광펜** — 키워드는 `linear-gradient(transparent 55%, #ffe066 55%)` 노랑 밑줄
6. ~~**고무도장**~~ — **제거** (2026-04-15 교사 피드백: 불필요). 스탬프·도장류 장식 모두 생략
7. **밑줄·화살표** — 중요 어휘 밑줄, 순서는 → 화살표로 연결
8. **말풍선** — 도입 멘트 말고 **보조 설명**에만 (교사 피드백: 도입 bubble 금지)
9. **빈칸** — `<span class="blank">&nbsp;</span>` 빈 span(CSS `border-bottom`으로 밑줄) + `min-width` 고정. **`____` 문자열을 span 안에 넣지 말 것** — 폰트 언더스코어와 border-bottom이 이중 밑줄로 겹쳐 보임 (2026-04-15 피드백). 정답은 작게 별도 표기
10. **최소 폰트 13pt 강제** (2026-04-17): CSS의 **모든** `font-size` 값이 13pt 이상이어야 함. `.cap`, `.hero-cap`, `.gl`, `.attribution-page code`, `.drafting` 등 캡션·부록류 포함. 12pt 이하 절대 금지.

**금지**:
- 학습목표 섹션 (교사용 문구, 학생 공책 불필요)
- 도입·호기심 유발 bubble
- 일반 고딕 폰트, 깔끔한 카드 UI, 사각 테두리 (교과서 집필진 톤)

## 한글 조판 규칙 (2026-04-15 교사 피드백)

- **낱말 단위 줄바꿈**: `body { word-break: keep-all; overflow-wrap: break-word; line-break: strict }` — 한국어는 어절 단위로만 개행, 글자 중간 끊기 금지
- **페이지 경계 잘림 방지**: 다음 요소에 `page-break-inside: avoid; break-inside: avoid` 필수
  - `.section, .grid6, .flow, .fill, .highlight, .kv, .gcard, .fstep, .topbar, p, li`
- 섹션 타이틀은 본문과 같은 페이지에: `.section-title { page-break-after: avoid }`
- 내용이 A4(297mm)를 넘으면 `<section class="page">`를 추가해 자동 분할. 페이지별 상단 헤더·페이지 번호 유지
- **다중 페이지 분할**: notebook.json에 `splits: [idx1, idx2, ...]` 배열로 명시 — 각 인덱스 앞에서 페이지 끊김. 단일 분할은 `split_at: N`도 허용 (하위 호환)
- **items_grid 블록이 2개 이상 + 각 4+ cards** 일 때 한 페이지 overflow 자주 발생 → 블록마다 별도 페이지 배치 권장 (2026-04-15 L9 교사 피드백)

## 이미지 프레임 (2026-04-15 교사 피드백)

- `gcard` 이미지: **블록 단위 카테고리 판정** 후 그 블록 내 모든 카드에 **동일 크기** 적용 (2026-04-15 교사 규칙 확정):
  - 블록 내 이미지 aspect 중간값으로 카테고리 결정
  - **세로 긴** (ar < 0.85): **35×50mm** 고정 (L8 옛 자료 기준)
  - **정사각** (0.85 ≤ ar ≤ 1.25): **50×50mm** 고정 (L1 지형 6가지 기준)
  - **가로 긴** (ar > 1.25): **50×28mm** 고정 (L5 제주도 flow 기준)
  - 기본 object-fit: cover + 카드 중앙 정렬. 한 블록 안에서 카드 크기 편차 없음
  - **예외 `image_fit: "contain"`** — 블록 레벨로 지정 시 흰 여백 허용(letterbox). 인물·고지도·도안 등 **잘림 금지**가 필수인 경우 (2026-04-15 L9 이사부·안용복·의용수비대·최종덕 기준)
- `fstep` 이미지: 기본 24mm 고정 (flow는 대체로 풍경 사진)
- 같은 블록 내 카드 높이가 이미지별로 달라질 수 있음 — 자연스러운 공책 느낌
- `grid_cols` 자동 규칙: 항목 수가 **2개 또는 4개**면 **2열 배치** (2×1, 2×2). 그 외는 3열 기본

## 구조 지원 (notebook.json 확장)

- `items_grid`: 3×N 카드 그리드 (이미지+이름+설명+위치)
- `flow`: 단계 체인 (화살표로 연결된 미니 카드)
- 이미지 경로 프리픽스: `"ext:..."` → phase4 외부 이미지, 그 외 → phase1 교과서 삽화

## 입력

- `phase3/notebook_draft.approved.md` + `phase2/notebook.json` (구조화 원본)
- `phase4/image_map.json`, `phase4/images/`
- `../../template.html` (스켈레톤)

## 산출

- `phase5/notebook.html` — 상대경로 이미지
- `phase5/notebook.standalone.html` — 이미지 base64 임베드 (Chromium file:// 이슈 회피용, phase6에서 사용)

## Primary Tool

**Jinja2 + mistune** — Python 네이티브, 한글 안전, 루프 자연스러움.

```bash
pip install jinja2 mistune
```

## 핵심 코드

```python
from jinja2 import Environment, FileSystemLoader
import json, base64, mimetypes, pathlib

note = json.load(open("phase2/notebook.json", encoding="utf-8"))
img_map = json.load(open("phase4/image_map.json", encoding="utf-8"))

# 이미지 base64 임베드 (Chromium file:// 한글경로 이슈 회피)
for block_id, img in img_map.items():
    m = mimetypes.guess_type(img["file"])[0] or "image/jpeg"
    data = base64.b64encode(open(img["file"], "rb").read()).decode()
    img["data_uri"] = f"data:{m};base64,{data}"

env = Environment(loader=FileSystemLoader("templates"), autoescape=True,
                  trim_blocks=True, lstrip_blocks=True)
html = env.get_template("notebook.html.j2").render(note=note, img_map=img_map)
pathlib.Path("phase5/notebook.standalone.html").write_text(html, encoding="utf-8")
```

## 템플릿 예시 (`notebook.html.j2`)

```jinja
{% extends "base.html.j2" %}
{% block pages %}
{% for page in note.pages %}
<section class="page">
  <div class="top-bar">
    <div>
      <div class="unit-tag">{{ note.subject_grade }} ▸ {{ note.unit_name }}</div>
      <div class="chapter-title">{{ page.chapter_title }}</div>
      <div class="date-line">{{ page.lesson_num }}차시 ─ {{ page.lesson_question }}</div>
    </div>
    <div class="page-ref">교과서 p.{{ page.page_from }}~{{ page.page_to }}</div>
  </div>

  <div class="goals"><strong>◎ 학습 목표</strong> ─ {{ page.goal }}</div>

  <div class="grid">
    <div class="block">
      <h3>{{ page.section_a.title }}</h3>
      {% for b in page.section_a.blocks if b.checked %}
        {% if b.type == "keyword_def" %}
          <div class="kv"><span class="k">{{ b.keyword }}</span>
            <span class="v">: {{ b.explanation }}</span></div>
        {% elif b.type == "callout" %}
          <div class="callout">{{ b.text }}</div>
        {% endif %}
      {% endfor %}
    </div>
    <div class="block">
      {% set img = img_map.get(page.id ~ ".section_b") %}
      {% if img %}
      <div class="image-slot">
        <img src="{{ img.data_uri }}" alt="{{ img.alt_text }}">
        {# 2026-04-17 정책: 이미지 출처·위치 캡션 렌더 금지 (image-scout.md 161 — 출처 표기 불필요).
           source_detail / attribution / license는 image_map.json에 내부 기록용으로만 보존. HTML·PDF에 출력하지 말 것. #}
      </div>
      {% endif %}
    </div>
  </div>

  {% for b in page.bubbles if b.checked %}
    <div class="bubble">💬 {{ b.speaker }}: "{{ b.text }}"</div>
  {% endfor %}

  {% if page.fill_blank %}
    <div class="fill-blank">
      {{ page.fill_blank.sentence | replace("___", '<span class="blank">' ~ page.fill_blank.answer ~ '</span>') | safe }}
    </div>
  {% endif %}

  <div class="footer">✎ p.{{ loop.index }}</div>
</section>
{% endfor %}
{% endblock %}
```

## 빈칸 정리(fill_blank) 단독 페이지 금지 (2026-04-17)

`fill_blank` 블록만 있는 페이지를 만들지 않는다. fill_blank는 반드시 다른 콘텐츠(keyword_def, items_grid, flow 등)와 **같은 페이지**에 배치한다. 내용이 부족해 페이지가 비어 보이면, 이전 페이지의 하단에 fill_blank를 붙인다.

- 잘못된 예: 2페이지 상단에 fill_blank 1개만 덩그러니 → 1페이지 하단으로 이동
- 올바른 예: 농작물 변화 items_grid + fill_blank가 같은 페이지에 함께 배치

## flow_arrow 커스텀 구분자 (2026-04-17)

notebook.json의 flow 블록에 `flow_arrow` 필드가 있으면 해당 문자를 단계 사이 구분자로 사용한다. 없으면 기본값 "→".

```json
"flow_arrow": "<"   // 크기 비교: 중강진 < 서울 < 서귀포
"flow_arrow": "→"   // 순서: 발원지 → 중류 → 하구 (기본값)
"flow_arrow": ">"   // 역순 비교
```

렌더 시 `.farrow` 요소의 텍스트를 `flow_arrow` 값으로 대체한다.

## CSS 배경 — notebook_bg.png data URI 사용 (2026-04-17)

줄 공책 배경은 `repeating-linear-gradient`가 아니라 **미리 생성한 notebook_bg.png를 data URI로 임베드**한다. PDF 열기 속도가 크게 개선됨 (gradient 수백 줄 반복 렌더 회피).

```css
.page {
  background-image: url('data:image/png;base64,...');  /* notebook_bg.png */
  background-size: 210mm 297mm;
  background-repeat: repeat;
}
```

- `notebook_bg.png`는 210mm x 297mm, 아이보리 바탕 + 가로 줄 + 왼쪽 빨간 마진선 포함
- gradient 기반 줄 배경 CSS는 사용하지 않는다

## items_grid loc 빈 문자열 시 pin 미출력 (2026-04-17)

`items_grid` 카드의 `loc` 필드가 빈 문자열(`""`)이거나 누락이면 `📍` 아이콘을 출력하지 않는다. `.gl` div 자체를 생략하거나 빈 채로 두되, `📍 ` 뒤에 아무 텍스트 없이 출력되는 일이 없어야 한다.

```python
# 렌더 시
if card.get("loc"):
    html += f'<div class="gl">📍 {card["loc"]}</div>'
# loc가 빈 문자열이면 .gl div 생략
```

## sub_kv 렌더 — keyword_def 하위 키워드 (2026-04-17)

notebook.json의 `keyword_def` 블록에 `sub_kv` 배열이 있으면, 상위 `.kv` 아래에 들여쓰기된 하위 키워드를 출력한다.

```html
<div class="kv"><span class="k">지구온난화</span> <span class="v">: 화석 연료 소비가 늘고...</span></div>
<div class="kv" style="margin-left:8mm"><span class="k">온실가스</span> <span class="v">: 이산화 탄소, 메탄 등...</span></div>
```

- `sub_kv` 내 각 항목을 `.kv` 동일 스타일로 렌더하되 `margin-left:8mm` 추가
- sub_kv가 없거나 빈 배열이면 무시

## section_title 선행 기호 자동 제거 (2026-04-17)

입력 JSON의 `section_title` 값에 선행 기호(`◆ ◇ ✦ ▶ ※ ★ ☆ ● ○ ◎`)가 포함되어 있으면 **렌더 시점에 반드시 strip**. CSS `.section-title.{diamond|gem|star|bullet}::before`가 기호를 자동으로 붙이므로, JSON에도 기호가 있으면 `◆ ◆`처럼 동일 기호 2연속으로 찍혀 feedback_no_double_asterisk 위반.

```python
def clean_title(s):
    if not s: return s
    s = s.lstrip()
    prefixes = "◆◇✦▶※★☆●○◎"
    while s and s[0] in prefixes:
        s = s[1:].lstrip()
    return s

# render 시: 반드시 래핑
f'<div class="section-title {color_cls}">{clean_title(b.get("section_title",""))}</div>'
```

content-curator 계약서도 JSON에 기호 넣지 말라고 명시돼 있지만, LLM이 실수할 수 있으므로 렌더러가 방어선이다.

## CSS 주의사항

- template.html의 CSS는 수정 금지 (스타일 표준 유지)
- 이미지 블록은 `.image-slot` 클래스만 사용
- **SVG·인라인 도안 직접 생성 금지** (v1 이슈 재발 방지)
- 한글 줄바꿈: `word-break: keep-all; overflow-wrap: break-word;`
- 페이지 나눔: `.block { break-inside: avoid; }` + 5~6블록/페이지

## HTML 검증

```bash
pip install html5validator
html5validator --root phase5/ --match "*.html"
```

## Fallback

- **Handlebars/Eta** (Node 스택 합칠 때)
- **Claude 직접 HTML 생성** (phase2 확장) — 단 수정·재렌더 비용↑ 비권장

## 허용 도구

`Read`, `Write`, `Edit`, `Bash`(Python + jinja2)

## 검증 게이트

- 모든 이미지 `src`가 data_uri 또는 실재 파일
- HTML 페이지 수 == draft 페이지 수
- `html5validator` 심각 오류 0
- 🗑 섹션·📝 교사 지시 섹션의 내용은 HTML에 포함되지 않음

## 실패 처리

- 이미지 경로 해석 실패 → 회색 `.image-placeholder` 박스 대체 + `_questions.md` 기록
- template 문법 오류 → 직전 커밋된 template 버전으로 롤백

## 참고

- https://jinja.palletsprojects.com/
- https://mistune.lepture.com/
