# Agent: draft-board-builder

**Phase**: 3 — draft-board
**역할**: phase2 구조화 JSON을 바탕으로 차시별 드래프트 공책보드를 렌더한다.

## 입력

- `phase0/request.json`
- `phase2/notebook.json`
- `phase2/notebook_{NN}.json`

## 산출

```text
phase3/
├── lesson_01.html
├── lesson_01.png
├── lesson_01.pdf
└── board_manifest.json
```

## 결과물 규칙

- 차시당 1장
- 실제 이미지는 삽입하지 않는다
- 이미지 자리에는 **프레임 상자**를 만들고, 내부에 `image_frame_prompt`를 짧은 설명문으로 넣는다
- phase2의 필수 비교·분류 항목은 살리되, 큰 범용 대표 이미지가 필수 항목 공간을 밀어내면 제거한다.
- “수도권 인구 집중” 같은 설명 블록 아래의 대형 도시 전경은 핵심 카드(일자리·의료·문화·주거·교통수단 등)보다 우선하지 않는다.
- 한 장이 빽빽해질 때는 핵심 항목 수를 줄이기보다, 큰 장식/범용 이미지와 중복 문장을 줄여 여백을 만든다.
- 공책정리처럼 보이되, 이 단계의 목적은 **내용 정확한 레퍼런스 보드 생성**이다
- phase4가 이 PNG를 `ima2`의 내용 앵커로 사용하므로, 텍스트가 선명해야 한다
- `fill_blank`는 학생 풀이용으로 빈칸만 보드에 남긴다. 정답, 초성 힌트, 답안 안내는 최종 보드에 표시하지 않는다.

## Primary Tool

**Jinja2 + Playwright**

- HTML 템플릿으로 보드 생성
- Playwright로 PNG/PDF 내보내기

## 검증 게이트

- 모든 차시에 PNG 생성
- 모든 차시에 프레임 상자 최소 1개 이상 존재
- 텍스트가 이미지 없이도 읽히는 수준

## 실패 처리

- 글자 과밀 → 줄 수/폰트/블록 수 조정 후 재렌더
- 프레임 설명이 너무 길어 잘림 → 설명문 축약 후 재렌더
