# Agent: textbook-extractor

**Phase**: 1 — extract
**역할**: 교과서 PDF에서 원문 텍스트·삽화를 bbox 기반으로 추출해 phase2·phase4에 전달.

## 입력

`tasks/{task_id}/phase0/request.json`

## 산출

```
tasks/{task_id}/phase1/
├── text.txt                    # 전체 원문
├── text_by_page/p{NNN}.txt    # 페이지별 분할
├── extract.json                # bbox 포함 구조화
├── images/                     # 추출 이미지 (PNG)
│   └── p{NNN}_{idx}.png
└── image_manifest.json         # 이미지 카탈로그
```

## Primary Tool

**PyMuPDF (fitz)** — 한 라이브러리로 텍스트·이미지·bbox·레이아웃 처리.

### 품질 비교 (한글 교과서 기준)
| 도구 | 레이아웃 | 한자·한글 | 속도 | bbox |
|---|---|---|---|---|
| pdftotext -layout | 2단 섞임 | 일부 손실 | 빠름 | ✗ |
| pdfplumber | 표 우수 | 줄바꿈 난삽 | 느림 | ✓ |
| **PyMuPDF blocks** | **자연스러움** | **정확** | **빠름** | **✓** ★ |
| docling | 최상 | 정확 | 느림 + 2GB 모델 | ✓ |

## 핵심 코드

```python
import fitz, json, pathlib

doc = fitz.open(req["textbook_pdf_path"])
pf, pt = req["page_range"]["from"], req["page_range"]["to"]
out = {"pages": []}

for pno in range(pf - 1, pt):
    page = doc[pno]
    # 텍스트 블록
    texts = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] == 0:  # text
            t = " ".join(s["text"] for l in b.get("lines", []) for s in l["spans"])
            texts.append({"bbox": list(b["bbox"]), "text": t})
    # 이미지
    images = []
    for i, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n - pix.alpha >= 4:  # CMYK → RGB
            pix = fitz.Pixmap(fitz.csRGB, pix)
        fn = f"phase1/images/p{pno+1:03d}_{i}.png"
        pix.save(fn)
        rects = page.get_image_rects(xref)
        images.append({
            "id": f"img_p{pno+1:03d}_{i:02d}",
            "file": fn,
            "bbox": list(rects[0]) if rects else None,
            "page": pno + 1,
        })
    out["pages"].append({"page": pno + 1, "texts": texts, "images": images})

json.dump(out, open("phase1/extract.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
```

## 이미지-본문 근접 매칭 (phase2에서 활용)

```python
def nearest_text(img_bbox, texts):
    ix, iy = (img_bbox[0] + img_bbox[2]) / 2, (img_bbox[1] + img_bbox[3]) / 2
    return min(texts, key=lambda t: (
        ((t["bbox"][0] + t["bbox"][2]) / 2 - ix) ** 2 +
        ((t["bbox"][1] + t["bbox"][3]) / 2 - iy) ** 2
    ))
```

## Claude Vision으로 이미지 caption 자동 생성

```python
import anthropic, base64

def caption(img_path):
    img64 = base64.b64encode(open(img_path, "rb").read()).decode()
    msg = anthropic.Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=200,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64",
             "media_type": "image/png", "data": img64}},
            {"type": "text", "text": "이 교과서 삽화를 초등 5학년이 이해할 수 있게 1문장으로 설명해. 종류(map/photo/illustration/diagram/icon)도 추측해줘. JSON으로 {caption, content_type}."}
        ]}]
    )
    return msg.content[0].text  # JSON 파싱
```

## Fallback

- **스캔본 OCR**: PaddleOCR (`korean` 모델, 인식률 96%) — `pip install paddlepaddle paddleocr`
- 대량 배치는 `pdfimages -png` 가 fitz보다 2배 빠름 (품질은 비슷)
- 벡터 이미지(SVG류)는 `get_images` 누락 → `page.get_pixmap(matrix=fitz.Matrix(3,3), clip=rect)` 로 300dpi 렌더 크롭

## image_manifest.json 스키마

```json
{
  "task_id": "...",
  "copyright_notice": "학교 교육 목적 이용. 대외 배포 시 출처 표기 필수.",
  "images": [{
    "id": "img_p010_01",
    "file": "images/p010_01.png",
    "page": 10, "bbox": [x0,y0,x1,y1],
    "width": 800, "height": 600,
    "caption": "한반도 지도 — 남한·북한 산지 분포",
    "content_type": "map",
    "nearest_text": "우리나라는 국토의 약 70%가 산지이다...",
    "usable": true
  }]
}
```

## 허용 도구

`Read`, `Write`, `Bash` (pymupdf Python, pdfimages, identify ImageMagick, exiftool)

## 검증 게이트

- `text.txt` 비어있지 않음 (또는 `needs_ocr=true` 플래그)
- `extract.json` 파싱 가능 + pages[] 길이 == page_range 범위
- `images/` 디렉토리 파일 존재 (차시 1개당 최소 1개 권장)
- `image_manifest.json` images[] 가 실제 파일과 1:1 매칭

## 실패 처리

- PDF 암호 → phase0에 에스컬레이션
- pdfimages 실패 → manifest.empty=true 플래그, phase4에서 외부 서치 비중 ↑
- Vision API 실패 → caption 필드 빈 문자열, phase2 LLM이 주변 텍스트로 대체 추정

## 참고

- https://pymupdf.readthedocs.io/en/latest/recipes-images.html
- https://docs.anthropic.com/en/docs/build-with-claude/vision
- https://github.com/PaddlePaddle/PaddleOCR
