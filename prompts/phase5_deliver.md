# Phase 5 — deliver

**에이전트**: dispatcher (`agents/dispatcher.md`)

## 목적
최종 차시별 PNG를 OneDrive로 배송하고, 배송 기록을 남긴다.

기본 산출물 경로:
`C:\Users\심보승\OneDrive - 남선초등학교\학습자료\사회\공책정리`

## 입력
- `phase0/request.json`
- `phase4/{과목}{학년}-{학기}_{단원번호}단원_{NN}차시_{lesson_title}.png`

## 산출
- `phase5/output/*.png`
- OneDrive 경로에 PNG 복사
- `phase5/manifest.sha256`
- `phase5/DELIVERED.md`
- (선택) `phase5/notebook_bundle.pdf`

## 실행기
`python3 scripts/phase5_deliver_png.py {task_id}`

## 검증 게이트
- OneDrive 경로에 복사본 존재
- sha256 기록 존재
- DELIVERED.md 생성
