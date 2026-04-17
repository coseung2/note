# Agent: reviewer

**Phase**: 4.5 — cross-lesson review
**역할**: 단원 전체(모든 차시)를 일괄 점검해 스타일·무결성 위반 탐지. Phase 5 진입 전 교사 확인용 리포트 생성.

## 입력

- `tasks/{task_id}/phase2/notebook_{NN}.json` (전 차시)
- `tasks/{task_id}/phase2/preview_{NN}.html` (전 차시)
- `tasks/{task_id}/phase4/images/` (외부 이미지)
- `tasks/{task_id}/phase1/images/` (교과서 이미지)
- `agents/html-builder.md`, `agents/content-curator.md`, `agents/image-scout.md` (기준 계약서)
- 메모리: `feedback_notebook_style.md`, `feedback_no_ai_doodles.md`

## 산출

- `tasks/{task_id}/phase_review/report.md` — 차시별 이슈 목록
- `tasks/{task_id}/phase_review/auto_fixes.json` — 자동 수정 가능한 항목 목록 (선택)

## 점검 항목 (2026-04-15 기준)

### A. 이미지 무결성
- [ ] 모든 `image_candidate_ids` / `items_grid[].image` / `flow[].image` 파일 실재 (phase1 또는 phase4)
- [ ] 이미지 파일 크기 ≥ 5KB (빈 파일·깨짐 탐지)
- [ ] PIL로 열기 성공 (손상 탐지)
- [ ] **PDF·문서 표지 오탐 탐지**: Gemini Vision으로 빠른 분류 — 'document cover', 'journal page', 'archive scan' 등이면 플래그
- [ ] 설명(`desc`)과 이미지가 의미 매치 (Vision 검증, 선택적)

### B. 프레임 카테고리 준수 (html-builder.md 기준)
- [ ] `items_grid` 블록 내 모든 카드 이미지 크기 **동일** (편차 없음)
- [ ] 블록 카테고리별 크기 일치: 세로긴 35×50mm / 정사각 50×50mm / 가로긴 50×28mm
- [ ] `flow` 이미지: 높이 24mm 통일
- [ ] `grid_cols` 자동 규칙: 2·4개면 2열, 그 외 3열

### C. 페이지 레이아웃
- [ ] 각 페이지 실측 높이 ≤ 297mm (A4 overflow 금지)
- [ ] `@page size: A4 portrait` 규칙 존재
- [ ] `page-break-inside: avoid` on section/grid/flow/fill
- [ ] `word-break: keep-all` 적용 (한글 어절 단위 줄바꿈)

### D. 타이포
- [ ] 최소 폰트 13pt (모든 `font-size:Npt`에서 N≥13)
- [ ] 금지 폰트: `Black Han Sans` 미사용
- [ ] 손글씨 폰트 로드 링크 존재 (Gaegu·Nanum Pen Script·Hi Melody)
- [ ] 캐시 방지 메타 태그 존재

### E. 콘텐츠 규칙 (content-curator.md 기준)
- [ ] `learning_goals` 필드 **없음** (제거됨)
- [ ] 도입성 bubble 없음 (교실 놀이·동기유발 멘트 제외)
- [ ] 🗑 제외 후보 섹션 존재 (프리뷰 하단 drafting)
- [ ] 모든 차시 `status: draft` 또는 `approved` 프론트매터

### F. 단원 전체 일관성
- [ ] 단원 타이틀 동일 (`unit_line`)
- [ ] 차시 번호 1~N 빠짐 없이 연속
- [ ] 차시 간 키워드 중복 없음 (또는 의도된 재등장만)

### G-0. 페이지 구성 (2026-04-17)
- [ ] **fill_blank 단독 페이지 없음** — fill_blank 블록만 있는 페이지가 존재하면 플래그. 다른 콘텐츠와 같은 페이지에 배치 필수.
- [ ] **items_grid loc 빈 문자열 시 pin 미출력** — `📍 </div>` 또는 `📍 <` 처럼 빈 위치 표시 탐지. loc가 비어있으면 `.gl` div 자체가 생략되어야 함.

### G. 장식 제거 (2026-04-15 확정)
- [ ] **마스킹테이프 제거** (`<div class="tape">` 미출력)
- [ ] **고무도장 제거** (`<div class="stamp">` 미출력)

### H. 기호 2연속 금지 (2026-04-17 feedback_no_double_asterisk)
- [ ] 렌더 HTML에 `◆ ◆` / `◇ ◇` / `✦ ✦` / `▶ ▶` / `※ ※` 등 **동일 기호 2연속 출력** 없음 — CSS ::before와 텍스트 기호 중복 탐지
- [ ] `**...**` 마크다운 이중 별표 HTML·JSON 모두 0건
- [ ] 같은 이유로 `~~`, `__`, `==` 등 이중 기호 0건
- [ ] notebook_NN.json의 `section_title` 값에 선행 기호(`◆ ◇ ✦ ▶ ※ ★ ☆ ● ○ ◎`) 포함 없음 (content-curator가 넣지 말아야 할 것이 들어갔는지 역검증)

### I. 무관 이미지 검출 (2026-04-17)
- [ ] keyword_def 블록의 `image_candidate_ids`에 있는 이미지가 **해당 블록의 keyword/explanation 개념과 의미적으로 일치**하는지 확인
  - 불일치 예: "기후 특징" 블록에 홍수(도로 유실) 사진, "꽃샘추위" 블록에 서리 맞은 식물 사진
  - **"대충 비슷해 보이는" 매핑 감지 시 플래그** — 텍스트 정의만으로 충분한 블록이면 이미지 제거 권고
- [ ] items_grid 카드의 image가 해당 카드의 name/desc와 의미 매치하는지 확인 (특히 교과서 삽화 자동 배정 시)

### J. 최소 폰트 13pt 확인 (2026-04-17)
- [ ] 모든 CSS `font-size:Npt`에서 N ≥ 13 (D 카테고리 기존 13pt 규칙을 **캡션·부록·코드 포함으로 확장**)
- [ ] `.cap`, `.hero-cap`, `.attribution-page code`, `.drafting li` 등 작은 폰트 사용 구간 전수 검사

## 체크 코드 예시

```python
import json, re, pathlib
from PIL import Image

def check_lesson(task_dir, n):
    p2 = task_dir/f"phase2/notebook_{n:02d}.json"
    html = (task_dir/f"phase2/preview_{n:02d}.html").read_text(encoding="utf-8")
    nb = json.load(open(p2))
    issues = []

    # 이미지 무결성
    for b in nb["blocks"]:
        for iid in collect_image_ids(b):
            path = resolve(iid, task_dir)
            if not path.exists():
                issues.append(("missing_image", iid))
                continue
            if path.stat().st_size < 5000:
                issues.append(("tiny_image", iid, path.stat().st_size))
                continue
            try: Image.open(path)
            except: issues.append(("corrupt_image", iid))

    # 폰트 검사
    fonts = set(re.findall(r"font-size:(\d+(?:\.\d+)?)pt", html))
    small = [f for f in fonts if float(f) < 13]
    if small: issues.append(("small_font", sorted(small)))

    if "Black Han Sans" in html:
        issues.append(("forbidden_font", "Black Han Sans"))

    # 장식 제거
    if '<div class="tape' in html: issues.append(("tape_present",))
    if '<div class="stamp"' in html: issues.append(("stamp_present",))

    # 캐시 방지
    if "Cache-Control" not in html: issues.append(("no_cache_meta_missing",))

    return issues
```

## 허용 도구

`Read`, `Bash` (PyMuPDF, PIL, requests), `Write`, `WebFetch`

## 실패 처리

- 이슈 수 > 0 → `report.md` 작성, 오케스트레이터에 반환
- 자동 수정 가능 항목(예: 캐시 메타 누락, 작은 폰트 일괄 상향): `auto_fixes.json`에 기록
- 심각한 이슈(이미지 깨짐, 파일 누락) → 교사 확인 요청 (`_questions.md`)

## 출력 예시 (report.md)

```markdown
# Phase 4.5 Review — 2026-04-15-social-5-1-unit1

## 전체 결과
- 차시: 10개
- 총 이슈: 3
- 자동 수정 가능: 1
- 교사 확인 필요: 2

## 차시별

### L6 독도의 위치
- ❌ `ext_l6_독도.jpg` — image aspect 2.65 > 1.25, 블록 카테고리 "가로긴"으로 판정됨. 다른 2장(동도·서도 portrait 0.7)과 불일치. 해결: `image_fit: contain` 또는 블록 분할

### L8 옛 기록
- ⚠️ small font: 11pt detected in `.drafting`. 허용 범위 외. 자동 수정 가능
```
