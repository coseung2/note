# Agent: pdf-renderer

**Phase**: 6 — pdf
**역할**: HTML → PDF 렌더링 + 검증.

## 입력

`tasks/{task_id}/phase5/notebook.standalone.html`

## 산출

- `phase6/notebook.pdf`
- `phase6/render.log`

## Primary Tool

**Playwright (Chromium)** — snap chromium 제약 회피, 웹폰트·CSS 최신 완전 지원.

```bash
pip install playwright
playwright install chromium
```

## 입력 소스 (2026-04-17 확정)

**preview HTML을 직접 PDF 변환한다.** `phase5/render_final.py`로 별도 렌더하지 않는다.
- 소스: `phase2/preview_{NN}.html` (교사 승인본, 최신 렌더러 반영)
- 이유: render_final.py와 render_preview.py가 별도 코드로 존재하면 수정사항 동기화 누락이 반복됨. preview = WYSIWYG 원칙.
- 이미지: preview가 상대경로(`../phase1/images/...`)를 쓰므로 `file://` 프로토콜로 열면 Playwright가 로컬 이미지를 정상 로드함.

## 핵심 코드

```python
from playwright.sync_api import sync_playwright
import pathlib

html_path = pathlib.Path("phase2/preview_01.html").resolve()  # preview 직접 사용

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file://{html_path}")
    page.emulate_media(media="print")
    # 폰트·이미지 로드 대기
    page.wait_for_function("document.fonts.ready")
    page.wait_for_load_state("networkidle")
    page.pdf(
        path="phase6/notebook.pdf",
        format="A4",
        margin={"top":"0mm","bottom":"0mm","left":"0mm","right":"0mm"},
        print_background=True,
        prefer_css_page_size=True,
    )
    browser.close()
```

## 한글 폰트 전략

템플릿 HTML에 `@font-face`로 로컬 TTF 로딩 (오프라인 안전):

```css
@font-face {
  font-family: 'Pretendard';
  src: url('file:///mnt/c/Windows/Fonts/Pretendard-Regular.otf') format('opentype');
}
@font-face {
  font-family: 'Gaegu';
  src: url('file:///mnt/c/Windows/Fonts/Gaegu-Regular.ttf') format('truetype');
}
```

추천:
- **Pretendard** (본문, SIL OFL) — 한글 가독성 최고
- **Gaegu / Nanum Pen Script** (학생 공책 느낌)
- **카페24 당당해체** (강조용)

## WSL snap chromium 회피

- **Playwright 자체 번들 사용** (위 코드) — 권장
- Windows Edge 직접 호출 fallback:

```bash
WEDGE="/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
"$WEDGE" --headless --disable-gpu \
  --print-to-pdf="/mnt/c/temp_claude/out.pdf" \
  --print-to-pdf-no-header \
  "file:///mnt/c/temp_claude/work.html"
```

## PDF 검증

```bash
pdfinfo phase6/notebook.pdf | grep -E "Pages|Page size"
qpdf --check phase6/notebook.pdf

# A4 크기 검증 (595 x 842 pt)
python -c "
import fitz
d = fitz.open('phase6/notebook.pdf')
p = d[0].rect
assert abs(p.width - 595) < 2 and abs(p.height - 842) < 2, 'Not A4'
print(f'OK: {d.page_count} pages, A4')
"
```

## Fallback

- **WeasyPrint** — 순수 Python, 빠름. CSS Grid·최신 webfont 약함. 텍스트만 있는 공책엔 OK
- **Edge headless** — snap 이슈 전부 회피, Windows 필수
- **PrinceXML** — 품질 최고, 유료. 교사 1인 환경엔 과투자

## 허용 도구

`Bash` (python + playwright, chromium-browser, msedge, pdfinfo, qpdf), `Read`, `Write`

## 검증 게이트

- PDF 파일 크기 > 0
- `pdfinfo` Pages 수 == 입력 HTML의 page 수
- 페이지 크기 A4 (595 × 842 pt)
- `qpdf --check` 오류 없음
- render.log에 Chromium fatal 없음

## 실패 처리

- 폰트 로드 실패 → 로컬 `fonts/` 폴더 TTF + `@font-face` 로 재시도
- Chromium crash → Edge headless로 전환
- 3회 실패 → 오케스트레이터 에스컬레이션 + `_questions.md` 작성

### 자주 발생 이슈
- **페이지 여백 무시** → `prefer_css_page_size=True` + `@page` CSS 양쪽 지정
- **이미지 첫 렌더 누락** → `networkidle` 대기 필수
- **빈 꼬리 페이지** → 마지막 블록 뒤 `<div style="page-break-after:avoid"></div>`

## 참고

- https://playwright.dev/python/docs/api/class-page#page-pdf
- https://pretendard.typepower.kr/
