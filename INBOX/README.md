# note/INBOX — 외부 요청 수신함

이 폴더는 **상위 ideation dispatcher가 새 공책정리 작업 요청을 보내는 입구**다.

## 사용 규칙

- ideation의 phase7 dispatcher만 이 폴더에 쓰기 권한 (외부 프로젝트 INBOX 쓰기 예외)
- note 프로젝트의 오케스트레이터가 INBOX를 주기적으로 확인 후 `tasks/{task_id}/`로 흡수
- 흡수 완료된 INBOX 항목은 `INBOX/processed/` 하위로 이동 (감사 이력)

## 받는 데이터 포맷

```
INBOX/{YYYY-MM-DD-slug}/
├── request.json          # phase0 표준 입력 스펙
├── source.pdf            # 교과서 PDF (또는 경로 참조)
└── handoff_note.md       # ideation에서 어떤 결정으로 넘어왔는지 컨텍스트
```

## 흡수 흐름

1. 오케스트레이터가 `INBOX/*/request.json` 발견
2. `tasks/{task_id}/phase0/` 생성 후 request.json 복사
3. phase1부터 정상 파이프라인 진입
4. 처리 시작 후 INBOX 원본은 `INBOX/processed/{task_id}/`로 이동
5. 완료 시 ideation 측에 ack 알림 (선택)

## 직접 사용 시

ideation 경유 없이 사용자가 직접 작업을 시작하는 경우, INBOX를 거치지 않고 Claude Code에 자연어로 요청하면 됨. 오케스트레이터가 직접 `tasks/`에 task_id 폴더 생성하고 phase0 진입.
