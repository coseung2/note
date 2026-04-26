# Phase 4 — stylize

**에이전트**: ima2-stylizer (`agents/ima2-stylizer.md`)

## 목적
style reference + phase3 draft-board를 사용해 `ima2`로 최종 차시별 공책정리 이미지를 생성한다.

## 입력
- `phase0/request.json`
- `phase3/lesson_{NN}.png`

## 산출
- `phase4/{과목}{학년}-{학기}_{단원번호}단원_{NN}차시_{lesson_title}.png`
- `phase4/requests.json`
- `phase4/run.log`
- `phase4/prompts/{NN}.txt`

## 실행기
`python3 scripts/phase4_stylize_ima2.py {task_id} --style-ref <style.png>`

사회 5-1 2단원 주제2 이후 작업은 사용자가 승인한 9차시 결과물을 스타일 레퍼런스로 우선 사용한다.

```bash
python3 scripts/phase4_stylize_ima2.py {task_id} \
  --style-ref "/mnt/c/Users/심보승/OneDrive - 남선초등학교/학습자료/사회/공책정리/사회5-1_2단원_09차시_수도권에 인구가 집중하는 원인은 무엇일까요.png"
```

## 고정 설정
- 품질: `medium`
- 크기: `1536x2048`
- 포맷: `png`
- 모더레이션: `low`
- 개수: `1`

## 레퍼런스 순서
1. 스타일 레퍼런스
2. phase3 draft-board
3. 필요 시 교과서 보조 레퍼런스

## 스타일 제한
- 내용과 상관없는 다이어리식 꾸밈을 만들지 않는다.
- 꽃, 별, 이파리, 반짝이, 랜덤 스티커 등 장식용 요소는 금지한다.
- 메인 타이틀 앞에는 기호를 붙이지 않고, 얇은 박스·형광펜·라벨 테두리로 감싸 강조한다.
- 기호(◆, ◇, ✦, ▶, ※ 등)는 본문 안의 섹션 소제목, 핵심 키워드, 중요 문장 강조에만 제한적으로 사용한다.
- 시각 요소는 교과 내용 이해를 돕는 삽화, 지도, 도식, 강조 표시 중심으로 둔다.

## 검증 게이트
- lesson별 최종 PNG 생성
- requests.json에 실행 메타 기록
- 로그에 fatal 없음

## 다음 phase
→ phase5 (deliver)
