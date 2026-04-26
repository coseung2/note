# Agent: dispatcher

**Phase**: 5 — deliver
**역할**: 최종 차시별 PNG를 OneDrive에 배송하고, 필요 시 묶음 PDF도 함께 만든다.

기본 산출물 경로:
`C:\Users\심보승\OneDrive - 남선초등학교\학습자료\사회\공책정리`

## 입력

- `phase0/request.json`
- `phase4/lesson_{NN}.png`

## 산출

- OneDrive 경로에 차시별 PNG 복사
- `phase5/manifest.sha256`
- `phase5/DELIVERED.md`
- (선택) `phase5/notebook_bundle.pdf`

## 파일명 규칙

```text
{과목}{학년}-{학기}_{단원번호}단원_{NN}차시_{lesson_title}.png
예: 사회4-1_2단원_01차시_국가유산이 무엇인지 알아볼까요.png
```

- 묶음 PDF 생성 시:
  `{과목}{학년}-{학기}_{단원번호}단원_공책정리본.pdf`

## Primary Tool

**PowerShell via WSL interop + sha256sum**

## 검증 게이트

- OneDrive 경로에 복사본 존재
- manifest에 sha256 기록
- DELIVERED.md 생성

## 실패 처리

- 폴더 없음 → 자동 생성
- 동일 파일명 존재 → `_v2`, `_v3` suffix로 보존
- PDF bundle 실패 → PNG 배송은 성공으로 처리하고 경고만 남김
