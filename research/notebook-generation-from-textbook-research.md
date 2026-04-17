# 교과서 → 학생 공책정리 자동생성 파이프라인 리서치

**작성일**: 2026-04-15
**트리거**: 사회 5-1학기 1단원 공책정리본 자동생성 시도 → Canva `generate-design` 결과물이 "너무 교과서 같다"는 교사 피드백
**참조 디자인**: Canva DAHG3ZbLzMo (8페이지 A4, 기존 학생 공책정리 스타일)
**실패 산출물**: Canva DAHG3ua4maE (generate-design 자동생성, 교과서 톤 회귀)

---

## 1. 핵심 결론 (TL;DR)

1. **`generate-design`은 답이 아니다.** Canva generative API는 "교과서 PDF 같은" 디폴트 스타일로 회귀. 참조 디자인을 **Brand Template + Autofill API** 또는 **MCP editing-transaction**으로 변수화하는 게 정공법.
2. **MVP 권장 스택**: 교과서 PDF → `pdftotext` → LLM(Claude)로 `{keyword, desc, visual_hint}` JSON 추출 → 참조 캔바 디자인 복제 후 **`start-editing-transaction` + `perform-editing-operations`** 로 텍스트만 교체 → 손그림은 사전 큐레이션된 SVG 라이브러리에서 `visual_hint` 매칭.
3. **Brand Template Autofill API는 Canva Enterprise 전용**. 개발 용도로 신청 시 승인 가능. 안 되면 MCP editing operations로 우회(1차 현실적 경로).
4. **"학생 공책 같은" 무드 = 폰트+레이아웃 7할**. 손글씨 한글 폰트(나눔손글씨, 카페24 써라운드) + 파스텔톤 + 짧은 문장 + 손그림 아이콘 4축 필수. AI 자동 sketchnote 도구는 영문 일색이라 한국 초등 사회과 부적합.
5. **MVP 총 공수 2일**, Canva Pro($15/월) 수준에서 시작 가능. HTML/CSS + Puppeteer는 fallback.

---

## 2. 실패 원인 분석 — 왜 generate-design이 교과서처럼 나왔나

| 원인 | 근거 |
|---|---|
| **모델 디폴트 회귀** | 프롬프트 모호도가 높을수록 "정돈된 교과서/슬라이드" 톤으로 수렴. 복잡한 프롬프트일수록 일반적 결과물 생성. |
| **스타일 어휘 부재** | "공책정리"는 영문 LLM에 무의미. "hand-drawn doodle, pastel marker, sticky-note callout" 같은 영문 시각 어휘로 분해 필요. |
| **레퍼런스 미주입** | generate-design은 참조 디자인 ID를 수용하지 않음. 스타일 학습 경로 차단. |
| **손그림 자산 부재** | Canva AI는 레이아웃은 잘하지만 "어린이 손그림 지도" 특정 미감 일러스트 생성 불가. |
| **레이아웃 자유도** | 슬라이드형 그리드 선호. 공책의 비대칭/콜라주 배치 재현 불가. |

**결론**: 0→1 생성이 아니라, **참조 디자인을 "골격"으로 삼고 콘텐츠만 갈아끼우는 변환 파이프라인**으로 전환.

---

## 3. 기술 스택 옵션 비교

| # | 방식 | 스타일 보존 | 자동화 | 공수 | 비용 | 교사 재편집 |
|---|---|---|---|---|---|---|
| A | **Canva Brand Template + Autofill API** | ★★★★★ | ★★★★ | 중 | Enterprise(or 개발승인) | ★★★★★ |
| B | **Canva 디자인 복제 + MCP editing-operations** ⭐추천 | ★★★★ | ★★★ | 중 | Pro($15/월) | ★★★★★ |
| C | **HTML/CSS + Puppeteer PDF** | ★★★★★(완전 제어) | ★★★★★ | 상(초기) | 무료 | ★(PDF만) |
| D | **Google Slides API + 템플릿 복제** | ★★★ | ★★★★ | 중 | 무료 | ★★★★ |
| E | **LLM + DALL-E/Flux 이미지 합성** | ★★(불안정) | ★★ | 상 | API 종량제 | ★★ |
| F | **AI Sketchnote 서비스(NoteGPT 등)** | ★★(영문/일률적) | ★★★★★ | 하 | 무료~Pro | ★ |
| G | **Templated.io / IMG.LY** | ★★★★ | ★★★★ | 중 | $29/월~ | ★★ |

**평가**: 한국 초등 + 교사 재편집 + 참조 디자인 활용 3축에서 **A > B > C** 순. A가 막히면 B로.

---

## 4. 추천 MVP 파이프라인

```
[1] 교과서 PDF 입력 (사회 8쪽)
      ↓ pdftotext + 페이지 분할
[2] 페이지별 원문 텍스트
      ↓ Claude LLM (구조화 프롬프트)
[3] notebook_spec.json
    [{ page, section, blocks: [
        {type:"keyword_def", keyword:"민주주의", desc:"국민이 주인인 정치"},
        {type:"map_callout", region:"수도권", note:"인구 절반"},
        {type:"speech_bubble", speaker:"시민", text:"내 의견 말할래!"},
        {type:"fill_blank", sentence:"___은(는) 국민이 뽑는다."}
      ]}]
      ↓ 참조 디자인 복제 (get-design + duplicate)
[4] 새 디자인 ID
      ↓ start-editing-transaction
      ↓ perform-editing-operations(텍스트 노드 교체)
      ↓ upload-asset-from-url(SVG 손그림) → 이미지 노드 교체
      ↓ commit-editing-transaction
[5] 완성 디자인 → export-design(PDF) → OneDrive 저장
```

**도구별 공수**
- **[2]→[3] LLM 프롬프트 1차 작성**: 4시간
- **스타일 토큰 사전(`visual_hint` 카탈로그) 50개 큐레이션**: 4시간
- **[3]→[4] Canva MCP 호출 래퍼 작성**: 6시간
- **SVG 라이브러리 구축**: SVG Repo / Icons8 / DrawKit에서 한국 사회과 빈출 100개(지도, 사람, 건물, 화살표, 말풍선) → `keyword → svg_path` 매핑 JSON: 4시간

**총 MVP**: 2일 작업.

---

## 5. 참조 Canva 템플릿 활용 구체 전략 (Canva MCP 기준)

### 전략 A — Brand Template Autofill (Enterprise/개발승인 시)
1. 참조 디자인 DAHG3ZbLzMo를 Canva Enterprise에서 **Brand Template으로 등록**, 텍스트/이미지 노드를 `{{keyword_1}}`, `{{desc_1}}`, `{{icon_1}}` 형태 데이터필드로 마킹.
2. `GET /brand-templates/{id}/dataset`로 필드 목록 조회.
3. `POST /v1/autofills`에 `notebook_spec.json` → 필드 매핑 페이로드 전송.
4. 비동기 job 폴링 → 완료 시 새 디자인 URL 회수.

### 전략 B — Editing Transaction (Pro 계정) ⭐ 현실적 1순위
1. `create-design-from-candidate`로 참조 디자인 복제(또는 수동 복제).
2. `get-design-content(content_types:["richtexts"])`로 모든 텍스트 노드 ID·좌표 수집.
3. `start-editing-transaction(design_id)` → 트랜잭션 생성.
4. 페이지별로 `perform-editing-operations` 호출, 각 텍스트 노드의 content를 LLM 산출 keyword/desc로 교체.
5. 손그림: `upload-asset-from-url`로 SVG 업로드 후 기존 image 노드의 asset_id 교체.
6. `commit-editing-transaction` → `export-design(format=pdf)`.

**핵심 노하우**: 참조 디자인의 **노드 ID와 의미를 사전 매핑**한 "template manifest"를 한 번만 만들어두면 모든 차시 재사용. 즉 사람 손으로 한 번만 "이 노드=keyword, 이 노드=desc, 이 노드=지도 자리" 라벨링하면 끝.

---

## 6. 확장 아이디어

1. **교사 재사용 라이브러리**: 차시 공책정리를 `move-item-to-folder`로 학년/단원별 자동 분류 → 동학년 공유.
2. **타 과목 적용**: 과학(실험 흐름도), 국어(인물관계도) 별 참조 디자인 manifest 추가 → 동일 파이프라인 재활용.
3. **학생 맞춤형**: 같은 차시도 `난이도=쉬움/보통/심화` 파라미터로 LLM이 빈칸 개수·키워드 수 조절 → 3종 PDF 자동 발행.
4. **참쌤스쿨 프리셋**: 인디스쿨/참쌤스쿨의 비주얼씽킹 학습지(PPT 편집형) 스타일을 manifest로 흡수 → 한국 교사 친숙한 톤 즉시 확보.
5. **태블릿 열람 최적화**: 갤탭 S6 Lite A5 가로 모드 리사이즈 옵션(`resize-design` MCP). *메모리 참조: 기준 태블릿 = 갤탭 S6 Lite.*
6. **교사 1클릭 GUI**: Windows 트레이 앱 → "PDF 드롭" → OneDrive 알림 / Obsidian Excalidraw 동시 출력.

---

## 7. 다음 단계 제안

1. **Brand Template Autofill API 승인 가능 여부 문의** (Canva Developer Portal)
2. **참조 디자인 manifest 작성 실험**: DAHG3ZbLzMo의 8페이지 × 각 노드 라벨링 1회 수행 → 템플릿 가능성 검증
3. **LLM 프롬프트 프로토타입**: 교과서 1개 차시 텍스트 → `notebook_spec.json` 변환 프롬프트 엔지니어링
4. **SVG 라이브러리 초기 큐레이션**: 사회 1단원(국토·지형·독도) 빈출 30개 아이콘만 먼저
5. 위 4개 성공 시 → phase3 Ouroboros interview로 시드화 → padlet 또는 class 프로젝트로 이관 검토

---

## 8. 참고자료

**Canva API / MCP**
- [Canva Autofill guide](https://www.canva.dev/docs/connect/autofill-guide/)
- [Applying Canva Brand templates with Autofill API](https://www.canva.dev/blog/developers/applying-canva-brand-templates/)
- [Canva MCP Documentation](https://www.canva.dev/docs/mcp/)
- [Create design autofill job API](https://www.canva.dev/docs/connect/api-reference/autofills/create-design-autofill-job/)
- [Canva Image replacement (Apps SDK)](https://www.canva.dev/docs/apps/examples/image-replacement/)

**대안 도구**
- [Templated.io — Canva API alternative](https://templated.io/canva-api/)
- [IMG.LY — Canva Connect Alternative](https://img.ly/canva-alternative)
- [Puppeteer PDF generation](https://pptr.dev/guides/pdf-generation)
- [Cloudflare Browser Rendering — PDF](https://developers.cloudflare.com/browser-rendering/how-to/pdf-generation/)

**AI Sketchnote 서비스 (비교용)**
- [sketchnote.app](https://sketchnote.app/)
- [NoteGPT AI Sketchnotes Generator](https://notegpt.io/ai-sketchnotes-generator)
- [VisualNote AI](https://www.visualnoteai.space/)
- [StudyPDF — Textbook to Notes AI](https://studypdf.net/use-cases/textbook-to-notes-ai)
- [aipdfnotes.com](https://aipdfnotes.com/)

**SVG/아이콘 라이브러리**
- [SVG Repo Doodle Library](https://www.svgrepo.com/collection/doodle-library-hand-drawn-vectors/)
- [DrawKit education icons](https://www.drawkit.com/)

**한국 교사 커뮤니티 · 참고**
- [참쌤스쿨 3-6학년 사회·과학 비주얼씽킹 학습지](https://chamssaem.com/1503)
- [참쌤스쿨](https://chamssaem.com)
- [인디스쿨](https://indischool.com/)
- [요즘 교사를 위한 AI 수업 활용 가이드 (국립교원연수원)](https://book.nifos.go.kr/library/10110/contents/7621968)

**학술 자료**
- [NoTeeline: Real-Time Personalized Notetaking with LLMs — ACM IUI 2025](https://dl.acm.org/doi/10.1145/3708359.3712086)
- [Structured Output with Guided JSON — LLM 가이드](https://medium.com/@kimdoil1211/structured-output-with-guided-json-a-practical-guide-for-llm-developers-6577b2eee98a)

---

## 부록: 이번 실험 아티팩트

| 항목 | 경로/ID |
|---|---|
| 참조 원본 디자인 | Canva DAHG3ZbLzMo (8p, "사회 5-1학기 1단원 공책정리의 사본") |
| 교과서 PDF | `C:\Users\심보승\Downloads\1단원_교과서.pdf` (46p, 392MB) |
| 실패 산출물(교과서 톤) | Canva DAHG3ua4maE, PDF: `OneDrive - 남선초등학교\학습자료\사회\공책정리\사회5-1_1단원_공책정리본.pdf` |
| 실패 원인 | generate-design의 레퍼런스 미주입 + 스타일 어휘 모호 |
