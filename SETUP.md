# Notebook Workflow — 환경 설치

전체 파이프라인을 WSL2 + Windows 환경에서 돌리기 위한 최소 의존성.

## 한 줄 요약

```
fitz(intake/extract) → Claude tool_use(draft) → Obsidian(validate)
  → Wikimedia+Pillow(image) → Jinja2+mistune(render)
  → Playwright(pdf) → PowerShell+sha256(deliver)
```

## Python 의존성

```bash
pip install \
  pymupdf \
  anthropic \
  jsonschema \
  pillow \
  requests \
  jinja2 \
  mistune \
  playwright \
  fastapi uvicorn python-multipart \
  html5validator

playwright install chromium
```

## 시스템 의존성 (apt)

```bash
sudo apt install -y \
  poppler-utils \
  imagemagick \
  exiftool \
  qpdf \
  inotify-tools
```

## 선택 (스캔 교과서 대응)

```bash
pip install paddlepaddle paddleocr   # 한글 OCR (96% 인식률)
# 또는
sudo apt install -y tesseract-ocr tesseract-ocr-kor  # 더 가볍지만 한글 88%
```

## 한글 폰트

로컬 설치 (오프라인 안전):
- **Pretendard** (본문, SIL OFL) — https://pretendard.typepower.kr/
- **Nanum Pen Script** (학생 공책 느낌) — Google Fonts
- **카페24 당당해체** (강조, 무료 교육용) — https://fonts.cafe24.com/

Windows 폰트 디렉토리(`C:\Windows\Fonts\`)에 설치된 폰트는 WSL에서 `/mnt/c/Windows/Fonts/` 경로로 접근 가능 → `@font-face` 로컬 로딩.

## 환경변수

```bash
# ~/.bashrc
export ANTHROPIC_API_KEY="..."          # phase2, phase4(Claude Vision)
export WIKIMEDIA_USER_AGENT="NotebookWorkflow/1.0 (mallagaenge@gmail.com)"
export ONEDRIVE_SCHOOL="/mnt/c/Users/심보승/OneDrive - 남선초등학교"
```

## 검증

```bash
# 설치 확인 스크립트
python -c "import fitz, anthropic, PIL, jinja2, mistune, playwright; print('OK')"
which pdftotext pdfinfo convert exiftool qpdf inotifywait
playwright install --dry-run chromium
```

## 환경 특이사항 (WSL)

- **snap chromium 금지**: `/tmp`·한글 경로 접근 불가 → Playwright 자체 번들 또는 Windows Edge 사용
- **한글 경로 escape**: `/mnt/c/Users/심보승/OneDrive - 남선초등학교/...` 공백·한글 포함, bash 큰따옴표로 감싸기
- **OneDrive "요청 시 파일"**: 복사 직후 cloud-only 상태일 수 있음 → `attrib.exe -P +U` 로 항상 유지 강제

## Edge Fallback (Chromium 실패 시)

```bash
WEDGE="/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
"$WEDGE" --headless --disable-gpu \
  --print-to-pdf="/mnt/c/temp_claude/out.pdf" \
  --print-to-pdf-no-header \
  "file:///mnt/c/temp_claude/work.html"
```
