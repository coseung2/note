# Phase 3 — validation (교사 수동 게이트)

**에이전트**: 없음. 교사가 직접 편집.

## 목적
LLM이 고른 콘텐츠를 교사가 최종 확정. 투명성·주도성 보장.

## Primary Tool

**Obsidian + Tasks 플러그인** — 이미 교사 워크플로우에 존재, frontmatter `status:` 네이티브, `Ctrl+Enter` 단축키.

### 대안
- **VSCode Markdown Checkbox 확장** (`bierner.markdown-checkbox`)
- **FastAPI 1파일 웹 UI** — Obsidian 없는 공용 PC용

## 흐름
1. 오케스트레이터가 `phase2/notebook_draft.md`를 교사에게 전달 (Obsidian 알림)
2. 교사 편집:
   - 체크박스 `[x]` / `[ ]` 토글 (Ctrl+Enter in Tasks 플러그인)
   - 키워드·설명 문구 직접 수정
   - 🗑 섹션 항목 필요 시 본문으로 이동
   - 📝 섹션에 자유 지시 추가
   - 이미지 후보 중 사용할 것만 체크
3. 프론트매터 `status: draft` → `status: approved` 변경
4. `phase3/notebook_draft.approved.md`로 저장

## 자동 재개 (파일 감지)

```bash
# inotifywait로 status 변경 감지
inotifywait -m -e modify tasks/*/phase2/*.md | while read path action file; do
  status=$(awk '/^status:/{print $2; exit}' "$path$file")
  if [ "$status" = "approved" ]; then
    cp "$path$file" "${path/phase2/phase3}notebook_draft.approved.md"
    python pipeline.py resume phase4 --task-id "$(basename $(dirname $path))"
  fi
done
```

## 편집 가이드 (교사용 원페이지)

```markdown
# 공책정리 검토 가이드

1. 파일 상단 `status: draft` 확인
2. 페이지별로 훑으면서:
   - ✅ 체크된 `- [x]` = 공책에 포함
   - ❌ 체크 해제 `- [ ]` = 제외
   - 키워드·설명 문구 직접 고쳐쓰기 OK
3. 🗑 섹션에서 필요한 항목 → 본문으로 복붙
4. 📝 섹션에 자유 지시 ("말풍선 더 귀엽게" 등)
5. 🖼 이미지 후보에서 ★권장 표시된 것 우선, 필요 시 여러 개 체크
6. 전부 끝나면 frontmatter `status: approved`로 변경 후 저장
7. 자동으로 다음 단계 실행됨
```

## 미니 웹 UI (Obsidian 없을 때)

```python
# pip install fastapi uvicorn python-multipart
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pathlib

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def edit():
    md = pathlib.Path("phase2/notebook_draft.md").read_text(encoding="utf-8")
    return f'''<form method=post action=/save>
      <textarea name=md rows=40 cols=100>{md}</textarea>
      <button>승인</button>
    </form>'''

@app.post("/save")
def save(md: str = Form(...)):
    p = pathlib.Path("phase3/notebook_draft.approved.md")
    p.parent.mkdir(parents=True, exist_ok=True)
    # 프론트매터 status 자동 변경
    md = md.replace("status: draft", "status: approved")
    p.write_text(md, encoding="utf-8")
    return "approved. 파이프라인 재개됩니다."
# uvicorn app:app --host 0.0.0.0 --port 8000
```

## 예상 소요
8페이지 기준 5~10분

## 검증 게이트
- 파일 존재
- 프론트매터 `status: approved`
- 최소 1개 이상 `- [x]` 블록

## 실패 처리
- Windows/WSL 경로 깨짐 → `/mnt/c/Users/.../OneDrive - 학교/` 공백·한글 escape 필수
- Obsidian 편집 중 외부 저장 충돌 → `.obsidian/config` "always update internal links" off

## 다음 phase
→ phase4 (image-source)

## 참고
- https://publish.obsidian.md/tasks/
- https://man7.org/linux/man-pages/man1/inotifywait.1.html
