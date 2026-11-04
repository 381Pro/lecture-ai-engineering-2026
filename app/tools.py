"""第3回: エージェントに持たせるツール。

ここに書いた関数の docstring と型ヒントが、そのままモデルへの「ツールの説明文」になる。
説明文を書き換えると、モデルがツールを使うかどうか・どんな引数で呼ぶかが変わる。
"""

import json
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3


@cache
def load_glossary() -> list[dict]:
    with open(DATA_DIR / "glossary.json", encoding="utf-8") as f:
        return json.load(f)["terms"]


def _normalize(text: str) -> str:
    return text.casefold().replace(" ", "").replace("　", "")


def _names(entry: dict) -> list[str]:
    return [_normalize(entry["term"]), _normalize(entry["id"])] + [
        _normalize(a) for a in entry["aliases"]
    ]


def search_glossary(query: str) -> str:
    """講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。

    AIエンジニアリングの用語や、この講座（AIE2026）に固有の言葉について
    答える前に使うこと。query には調べたい用語を1つだけ入れる（例: "LoRA"）。
    """
    q = _normalize(query)
    if not q:
        return "検索語が空です。調べたい用語を1つ指定してください。"
    glossary = load_glossary()

    exact = [e for e in glossary if q in _names(e)]
    # 「r」のような短い別名が何にでも当たらないよう、名前側が短いものは除く
    partial = [
        e for e in glossary
        if e not in exact and any(q in n or (len(n) >= 3 and n in q) for n in _names(e))
    ]
    in_definition = [
        e for e in glossary
        if e not in exact and e not in partial and q in _normalize(e["definition"])
    ]
    hits = (exact + partial + in_definition)[:MAX_RESULTS]

    if not hits:
        return f"用語集に「{query}」は見つかりませんでした。"
    return json.dumps(
        [
            {
                "term": e["term"],
                "lecture": e["lecture"],
                "definition": e["definition"],
                "related": e["related"],
            }
            for e in hits
        ],
        ensure_ascii=False,
    )


def get_lecture_summary(lecture: int) -> str:
    """指定した回（1始まりの整数）の講義の要点を返す。

    「第3回では何を学ぶ？」のように、回の内容や関係を聞かれたときに使う。
    """
    path = DATA_DIR / "lectures" / f"{lecture:02d}.md"
    if not path.exists():
        available = sorted(p.stem for p in (DATA_DIR / "lectures").glob("*.md"))
        return f"第{lecture}回の要点はまだありません。用意されている回: {', '.join(available)}"
    return path.read_text(encoding="utf-8")


LEARNING_LOG_DIR = Path(__file__).resolve().parent.parent / "learning_log"


def make_quiz(term: str) -> str:
    """指定した用語について、定義から4択クイズを1問作る。クイズを作りたいときに使う。"""
    result = search_glossary(term)
    if "見つかりませんでした" in result:
        return result
    try:
        matches = json.loads(result)
    except ValueError:
        return result
    if not matches:
        return result
    target = matches[0]
    others = [t for t in load_glossary() if t.get("term") != target.get("term")][:3]
    if len(others) < 3:
        return "クイズを作るのに十分な用語がありません。"
    choices = [target["definition"]] + [t["definition"] for t in others]
    shift = len(target["term"]) % 4
    choices = choices[shift:] + choices[:shift]
    answer = "ABCD"[choices.index(target["definition"])]
    lines = [f"問題: 「{target['term']}」とは何か。最も適切な説明を選べ。"]
    lines += [f"{label}. {text}" for label, text in zip("ABCD", choices)]
    lines.append(f"答え: {answer}（{target['term']}）")
    return "\n".join(lines)


def save_learning_log(topic: str, content: str) -> str:
    """学習の記録を learning_log/ に Markdown ファイルとして保存する。保存する前に利用者の確認が必要。"""
    import re
    from datetime import date

    today = date.today().isoformat()
    safe = re.sub(r'[\\/:*?"<>|]', "", topic).strip().replace(" ", "_") or "log"
    LEARNING_LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LEARNING_LOG_DIR / f"{today}_{safe}.md"
    mode = "a" if path.exists() else "w"
    with path.open(mode, encoding="utf-8") as f:
        if mode == "a":
            f.write("\n---\n\n")
        f.write(f"# {topic}\n\n- 日付: {today}\n\n{content}\n")
    return f"保存しました: {path}"
