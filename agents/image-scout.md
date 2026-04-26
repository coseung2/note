# Agent: image-scout

**Phase**: 4 — image-source
**역할**: 교사 승인본에 따라 이미지 확정. 교과서 삽화 크롭 + 외부 CC/공공 이미지 서치·다운로드·라이선스 기록.

## 입력

- `phase3/notebook_draft.approved.md`
- `phase1/image_manifest.json`, `phase1/images/`

## 산출

```
tasks/{task_id}/phase4/
├── images/                     # 최종 사용 이미지 (가로 800px, JPG/PNG 최적화)
├── image_map.json              # 블록ID → 파일 + 메타
└── attribution.md              # 출처·라이선스 (PDF 말미에 삽입될 것)
```

## Primary Tool

**Pillow + requests + Wikimedia Commons API + ImageMagick/exiftool**

```bash
pip install pillow requests
sudo apt install imagemagick exiftool oxipng
```

## 공공 자료 URL 카탈로그 (한국 교과 맥락)

| 기관 | URL | 사용법 | 용도 |
|---|---|---|---|
| 국토지리정보원 국토정보플랫폼 | https://map.ngii.go.kr | 회원가입 후 shp/tif, 지도 캡처 허용 | 지리 교과 지형도 |
| 외교부 독도 누리집 | https://dokdo.mofa.go.kr | 공공누리 1유형 (출처 표시) | 독도 사진·지도 |
| 국가유산포털 | https://www.heritage.go.kr | OpenAPI `openapi.heritage.go.kr/openapi/json/GetKHeritageService` | 문화재 사진 |
| 공공데이터포털 | https://www.data.go.kr | API 키 필요 | 통계·지도 |
| 국가기록원 | https://www.archives.go.kr | 공공누리 표기 | 역사 사진 |
| Wikimedia Commons | https://commons.wikimedia.org/w/api.php | MediaWiki API | 범용 (학술 삽화) |
| NASA Images | https://images.nasa.gov | Public Domain | 우주·지구과학 |

## 핵심 코드 — Wikimedia API

```python
import requests, pathlib

HEADERS = {"User-Agent": "NotebookWorkflow/1.0 (mallagaenge@gmail.com)"}
ACCEPTABLE = ["CC0", "Public domain", "CC BY", "CC BY-SA"]

def wm_search(query, n=5, width=800):
    r = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        params={
            "action": "query", "format": "json",
            "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap",
            "gsrlimit": n,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": width,
        },
        headers=HEADERS,
    ).json()
    out = []
    for p in r.get("query", {}).get("pages", {}).values():
        info = p["imageinfo"][0]
        ext = info["extmetadata"]
        lic = ext.get("LicenseShortName", {}).get("value", "?")
        if not any(a in lic for a in ACCEPTABLE):
            continue
        out.append({
            "url": info["thumburl"],
            "license": lic,
            "author": ext.get("Artist", {}).get("value", "?"),
            "source": info["descriptionurl"],
            "title": p.get("title"),
        })
    return out

# 한글 1차 → 영문 2차 (Commons는 영어 학술명 hit률↑)
def search_both(ko, en):
    return wm_search(ko) + wm_search(en)
```

## 검색 쿼리 전략

- **1차**: 한글 원 키워드 (`식물 뿌리`) — hit ~20%
- **2차**: 영문 학술명 (`plant root`, `cross section`) — hit ~70%
- phase2 `image_search_query` 필드에 영어 쿼리 사전 생성 권장 (Claude가 phase2 시점에 번역)

## ImageMagick 후처리 (교과서 삽화 → 공책용)

```bash
# 흰 배경 trim + 800px 폭 + 품질 85
convert raw.png -trim +repage -resize 800x \
  -background white -alpha remove -quality 85 out.jpg

# 일괄 PNG 최적화
find phase4/images -name '*.png' -exec oxipng -o 4 --strip safe {} +
```

## 라이선스 자동 검증 + 메타 임베드

```bash
# IPTC 메타데이터 주입
exiftool -Credit="Wikimedia Commons" \
  -Source="https://commons.wikimedia.org/..." \
  -CopyrightNotice="CC BY-SA 4.0" \
  -overwrite_original out.jpg
```

```python
def license_ok(lic):
    return any(a in lic for a in ACCEPTABLE + ["공공누리"])
```

## 공공누리 이미지 (Commons 밖)

별도 메타 파일 `_meta.json` 수동 기재:

```json
{
  "file": "dokdo_1.jpg",
  "license": "공공누리 1유형",
  "author": "외교부",
  "source": "https://dokdo.mofa.go.kr/...",
  "required_attribution": "외교부, 공공누리 1유형"
}
```

## 이미지 교체 규칙 — 설명과 매치 필수 (2026-04-15 피드백)

이미지를 교체하거나 외부 서치로 보강할 때는 **블록의 `desc`·`explanation` 필드와 의미가 매치되는지 먼저 확인**한다. 설명에 특정 지형 특징(예: "육각형 바위기둥", "주상절리", "다도해", "하구")이 명시되어 있으면, 외관상 그 특징이 드러난 사진을 골라야 한다.

- 잘못된 예 (2026-04-15 L2 무등산): 설명 "화산 활동으로 만들어진 육각형 바위 기둥"인데 "광주 시가지 배경의 무등산 전경"으로 교체 → 주상절리 특징 안 드러나 재교체 요청
- 올바른 방식: 교체 전 설명 문구 re-read → 서치 쿼리에 특징어 포함 (예: "Mudeungsan Jusangjeolli columnar joints") → 결과 이미지를 Read 툴로 직접 확인 → 특징 드러나면 채택, 아니면 폐기
- **교과서 삽화가 설명에 이미 부합하면 교체하지 말 것**. 겉보기 화질만 낮아 보여도 의미 매치가 우선.
- **여백·배경이 과다할 때는 크롭으로 해결** (2026-04-15): 하늘이 지나치게 넓거나 주제 비중이 작으면 PIL로 상/하 일정 비율 자르고 `ext_l{N}_{이름}.jpg`로 저장. 외부 서치로 새 사진 찾기 전에 크롭 시도. 주요 피사체(주상절리·해안선 등)가 60~70% 면적 차지하도록.
- **다운로드 후 Read 시각 검증 필수** (2026-04-15): Wikimedia `gsrsearch`가 일반 키워드에서 PDF·djvu·IA 자료 표지 썸네일을 첫 결과로 반환하는 경우가 잦음(아카이브 문서). 매 다운로드 직후 파일을 Read 툴로 열어 실제 이미지인지 확인. PDF 표지·문서·flag/logo 감지 시 다음 결과로 재시도. 실패 결과 패턴: 'historic archived document', 'Congressional Research', 'Ulleungdo and Usando' (고지도) 등은 회피.
- **교과서 원본에 whole-subject 사진 존재 확인 우선** (2026-04-15 L6 독도): 외부 서치 전에 phase1 image_manifest에서 해당 페이지 주변의 큰 이미지(>500KB) 시각 확인. 섬·지형처럼 전체 피사체가 필요한 경우 특히 교과서에 aerial/panorama가 이미 있을 가능성 높음.

## `flow`·`items_grid` 구조 내 이미지 처리

notebook.json의 `flow[].image` 또는 `items_grid[].image` 필드가 **null** 이거나 명시적으로 외부 서치 요청인 경우, 각 단계·항목별로 개별 서치 수행 (2026-04-15 — 한강 flow의 "서울·황해" 케이스).

- null 단계 보고: content-curator가 `image`를 `null`로 둔 것은 "교과서에 없음" 표시 → image-scout가 검색어를 추론해 외부에서 수급
- 검색어 추론: 단계의 `name` + 상위 키워드(예: 한강) + 교과 맥락
  - "서울" + "한강" + 한국 초등 사회 → `"Seoul Han River aerial"` 또는 `"Seoul skyline Han River"`
  - "황해" + "한강" + 하구 → `"Han River estuary Ganghwa"` 또는 `"Yellow Sea Korea Han mouth"`
- 저장: `phase4/images/ext_{slug}.{ext}` 형식. image 필드를 `"ext:파일명"`으로 갱신
- attribution.md 필수

## 교과서 크롭 순도 (2026-04-17 feedback_textbook_crop_purity)

교과서 삽화를 크롭할 때, 블록 개념과 **무관한 이물 객체가 프레임에 들어가면 해당 삽화를 포기하고 웹 서치로 대체**한다.

**이물 객체 예시** (감지 즉시 폐기 대상):
- 학습 도우미 캐릭터 머리·손(돋보기 든 아이, 학생 캐릭터 등) — 프레임 귀퉁이에 살짝 나와도 포기
- 말풍선·대화 지문 박스
- "자료 가 / 자료 나" 같은 탭 라벨
- 페이지 번호, 퀴즈 아이콘, 장식 그래픽
- 인접한 다른 개념의 부분 삽화

**판정 절차:**
1. 크롭 후 `Read` 툴로 시각 검증
2. 체크: 블록 keyword/desc 개념 외 **다른 객체가 보이는가?** 정면·귀퉁이 모두 확인
3. 이물 감지 → 크롭 2회까지 재시도 (더 좁게). 여전히 이물이 남으면 **포기**
4. 포기 시 → 웹 서치(Google/Naver 우선)로 대체 이미지 확보
5. 대체 이미지도 Read 시각 검증

**예외**: 이물이 극소형이고 블록 중심을 전혀 가리지 않으며 웹 서치 대안이 없는 경우 — 교사 확인 필수.

2026-04-17 사례: L1 p6 "자료 나 지도" 크롭 시 우측 상단 돋보기 캐릭터 포함 → 크롭 포기하고 웹 서치로 대체.

## 소싱 우선순위

1. 교과서 삽화 (phase1 추출, 학교 교육 목적 이용)
2. 정부·공공기관 공개 자료 (공공누리)
3. **Google/Naver 이미지 검색** (2026-04-17 정책 변경: 한국 교육 맥락 사진은 Wikimedia보다 Google/Naver가 훨씬 풍부. 학교 교육 목적 내부 사용에 한정, 상업 배포·외부 공개 없음을 전제.)
4. Wikimedia Commons CC
5. Unsplash / Pexels (로열티프리, 인물 제외)
6. **AI 생성 이미지 / matplotlib 차트** (폴백) — 1~5에서 적절한 후보를 찾지 못한 경우에만.

**출처 표기 불필요** (2026-04-17 교사 지시). `attribution.md`는 내부 기록용 선택 사항. 최종 PDF에 출처 페이지 삽입 의무 없음.

**절대 금지**
- 타 교사 학습지 이미지 무단 사용 (개인 창작물)

## 교사 직접 URL 제공 워크플로우 (2026-04-17)

교사가 Google/Naver 검색에서 찾은 이미지 URL을 직접 지정할 수 있다. 이 경우:
1. 지정 URL을 `curl` 다운로드
2. Read 시각 검증 (깨졌거나 의도와 다르면 교사에게 보고)
3. `ext_l{N}_{slug}.{ext}` 명명
4. notebook JSON의 해당 블록 image 필드 갱신
5. attribution 기록 불필요

## image_map.json 스키마

```json
{
  "p1.section_a": {
    "file": "images/p1_section_a.jpg",
    "source_type": "textbook_crop",
    "source_detail": "교과서 p.10 삽화 (img_p010_01)",
    "license": "학교 교육 목적 이용 (저작권법 제25조)",
    "alt_text": "우리나라 지형을 나타낸 한반도 지도"
  },
  "p2.section_b": {
    "file": "images/p2_section_b.jpg",
    "source_type": "wikimedia_cc",
    "source_url": "https://commons.wikimedia.org/wiki/File:...",
    "license": "CC BY-SA 4.0",
    "author": "저작자명",
    "attribution": "저작자: OOO, 변경 없음, CC BY-SA 4.0",
    "alt_text": "지리산 원경 사진"
  },
  "p3.section_c": {
    "file": "images/p3_section_c.png",
    "source_type": "ai_generated",
    "alt_text": "광합성 과정을 단순화한 도식"
  }
}
```

## 허용 도구

`Read`, `Write`, `Bash`(convert, oxipng, exiftool), `WebSearch`, `WebFetch`

## 검증 게이트

- draft에서 체크된 블록 전부에 대응 이미지 존재
- 외부 이미지 전부 라이선스 정보 포함
- `attribution.md`의 출처 수 == 외부 이미지 수
- 모든 이미지 파일 크기 > 0 + 가로 800px 이상

## 실패 처리

- 1~4 후보 부적합 → AI 생성 이미지 폴백 시도 → 그래도 부적합하면 교사 에스컬레이션 ("이 블록 이미지 없이 진행?")
- 공공누리 페이지 스크레이핑 필요 시 robots.txt 준수
- 썸네일 404 → `iiurl` 원본으로 폴백

## 참고

- https://commons.wikimedia.org/wiki/Commons:API
- https://www.kogl.or.kr/ (공공누리)
- https://www.data.go.kr/tcs/dss/selectApiDataList.do
- https://images.nasa.gov
