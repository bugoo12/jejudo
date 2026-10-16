# -*- coding: utf-8 -*-
"""
제주도 가족여행 대시보드 — 프로젝트 요약(Markdown) 자동 저장 스크립트

data.json(대시보드 원본 데이터)을 읽어서 PROJECT_SUMMARY.md 파일로 저장합니다.
가족이 대시보드에서 일정/준비물을 업데이트한 뒤 다시 실행하면
요약도 항상 최신 상태로 다시 생성됩니다.

사용법:
    python save_summary.py
"""
import json
import sys
from pathlib import Path
from datetime import date, datetime

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "data.json"
OUT_FILE = BASE / "PROJECT_SUMMARY.md"

WEEKDAYS_KO = ["월", "화", "수", "목", "금", "토", "일"]
DASH_URL = "https://bugoo12.github.io/jejudo/"
REPO_URL = "https://github.com/bugoo12/jejudo"


def parse_date(s: str) -> date:
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)


def fmt_date(s: str) -> str:
    dt = parse_date(s)
    return f"{dt.month}/{dt.day} ({WEEKDAYS_KO[dt.weekday()]})"


def dday(s: str) -> str:
    delta = (parse_date(s) - date.today()).days
    if delta > 0:
        return f"D-{delta}"
    if delta == 0:
        return "D-Day 🎉"
    return "여행 종료 🌊"


def box(checked: bool) -> str:
    return "[x]" if checked else "[ ]"


def build_markdown() -> str:
    d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    meta = d["meta"]
    L: list[str] = []
    A = L.append

    # ── 머리말 ──────────────────────────────────────────────
    A("# 🌊 제주도 가족여행 대시보드 — 프로젝트 요약")
    A("")
    A(f"> 🖥️ **대시보드**: {DASH_URL} · "
      f"📅 **기간**: 2026.11.26 ~ 11.29 (3박 4일) · "
      f"⏰ **출발까지**: {dday(meta['startDate'])}")
    A("> 본 요약은 `save_summary.py`가 `data.json`을 읽어 자동 생성했습니다. "
      "(생성 시각: " + datetime.now().strftime("%Y-%m-%d %H:%M") + ")")
    A("")

    # ── 가족 구성 ──────────────────────────────────────────
    A("## 👨‍👩‍👧‍👦 가족 구성 (4인)")
    A("")
    A("| 이름 | 역할 |")
    A("|---|---|")
    for f in d["family"]:
        A(f"| {f['emoji']} {f['name']} | {f['role']} |")
    A("")

    # ── 사진 갤러리 (대시보드 메인) ─────────────────────────
    A("## 📸 여행 사진 갤러리 (대시보드 메인 — 빈 칸에 가족이 직접 넣어요)")
    A("")
    gal = d.get("gallery") or []
    if gal:
        for i, g in enumerate(gal, 1):
            src = g.get("src") or "*(빈 칸 — 대시보드 📷 칸에 사진 올리기)*"
            title = g.get("title") or "*(제목 미정 — 대시보드에서 클릭해서 입력)*"
            caption = g.get("caption") or " "
            A(f"{i}. **{title}** — {caption}")
            A(f"   - 이미지: {src}")
    else:
        A("- *(아직 없음 — 대시보드에서 ＋ 사진 칸 추가)*")
    A("")

    # ── 일정 ────────────────────────────────────────────────
    A(f"## 📅 일정 ({fmt_date(meta['startDate'])} ~ {fmt_date(meta['endDate'])}, 3박 4일)")
    A("")
    for day in d["days"]:
        A(f"### {day['label']} — {fmt_date(day['date'])} · {day['theme']}")
        A("")
        A("| 시간 | 일정 | 메모 |")
        A("|---|---|---|")
        for it in day["items"]:
            mark = "✅ " if it.get("checked") else ""
            note = it.get("note", "")
            if it.get("checked"):
                note = f"~~{note}~~" if note else note
            A(f"| {it['time']} | {mark}{it['title']} | {note} |")
        A("")

    # ── 준비물 ──────────────────────────────────────────────
    total = sum(len(c["items"]) for c in d["packing"])
    done = sum(1 for c in d["packing"] for i in c["items"] if i.get("checked"))
    A(f"## 🎒 준비물 ({done}/{total} 챙김)")
    A("")
    for cat in d["packing"]:
        c_done = sum(1 for i in cat["items"] if i.get("checked"))
        A(f"### {cat['icon']} {cat['category']} ({c_done}/{len(cat['items'])})")
        A("")
        for item in cat["items"]:
            A(f"- {box(item.get('checked'))} {item['text']}")
        A("")

    # ── 아이 플랜 ───────────────────────────────────────────
    A("## 👦👧 아이 플랜 (민준 11살 남 · 민지 8살 여)")
    A("")
    for kid in d["kidsPlan"]:
        A(f"### {kid['emoji']} {kid['name']} ({kid['age']}살)")
        A("")
        A("**💖 가고 싶은 곳**")
        for it in kid["wish"]:
            A(f"- {box(it.get('checked'))} {it['text']}")
        A("")
        A("**🎯 여행 미션**")
        for it in kid["mission"]:
            A(f"- {box(it.get('checked'))} {it['text']}")
        A("")
        A("**🌟 담당 역할**")
        for it in kid["duty"]:
            A(f"- {box(it.get('checked'))} {it['text']}")
        A("")

    # ── 여행 전 할 일 ───────────────────────────────────────
    t_done = sum(1 for i in d["todo"] if i.get("checked"))
    A(f"## ✅ 여행 전 할 일 ({t_done}/{len(d['todo'])} 완료)")
    A("")
    for it in d["todo"]:
        due = f" · 📅 기한 {it['due']}" if it.get("due") else ""
        A(f"- {box(it.get('checked'))} {it['text']}{due}")
    A("")

    # ── 메모 ────────────────────────────────────────────────
    A("## 📝 메모")
    A("")
    for m in d["memo"]:
        A(f"- **{m['title']}**: {m['content']}")
    A("")

    # ── 함께 업데이트하는 방법 ───────────────────────────────
    A("## 🤝 함께 업데이트하는 방법")
    A("")
    A("1. **대시보드에서 직접 수정** — 체크/수정/추가 후 **💾 GitHub에 저장** "
      "(최초 1회 ⚙️ 설정에서 GitHub 토큰 입력)")
    A("2. **GitHub 웹에서 편집** — [data.json 편집]("
      f"{REPO_URL}/edit/main/data.json) → 수정 후 Commit (토큰 불필요)")
    A("")
    A("두 방법 모두 저장 즉시 가족 모두의 화면에 반영됩니다 "
      "(접속 시 최신 로딩 + 30초마다 자동 동기화).")
    A("")

    # ── 파일 구성 ───────────────────────────────────────────
    A("## 📁 저장소 파일 구성")
    A("")
    A("| 파일 | 설명 |")
    A("|---|---|")
    A("| `index.html` | 가족 공유 대시보드 (GitHub Pages) |")
    A("| `data.json` | 모든 데이터의 원본 — 대시보드가 읽고 저장하는 파일 |")
    A("| `checklist.md` | 초기 스냅숏 체크리스트 (인쇄/GitHub 보기용) |")
    A("| `images/` | 갤러리 사진 폴더 — 대시보드 📤 버튼으로 업로드 시 자동 생성·커밋 |")
    A("| `save_summary.py` | 이 요약을 자동 생성하는 Python 스크립트 |")
    A("| `PROJECT_SUMMARY.md` | 본 파일 — 스크립트가 자동 생성 |")
    A("")
    A("## 🔄 요약 갱신하기")
    A("")
    A("```bash")
    A("python save_summary.py")
    A("```")
    A("")
    A("## ⏭️ 다음 할 일 (보류 중)")
    A("")
    A("- ✈️ 항공편 정보(편명·시간) 입력 대기 중 — 알려주시면 Day 1/Day 4 일정에 반영")
    A("- 숙소·렌터카 예약 확정 후 📝 메모 탭에 정보 기입")
    A("")
    A("---")
    A("")
    A("*자동 생성: `save_summary.py` · 원본 데이터: `data.json`*")

    return "\n".join(L) + "\n"


def main() -> None:
    md = build_markdown()
    OUT_FILE.write_text(md, encoding="utf-8", newline="\n")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(f"Saved: {OUT_FILE.name} ({len(md):,} chars, {md.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
