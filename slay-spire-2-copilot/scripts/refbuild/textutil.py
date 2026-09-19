"""Small text helpers shared by merge, codex, and census passes."""
import re


def has_cjk(s) -> bool:
    return bool(s) and bool(re.search(r"[一-鿿]", str(s)))


def humanize(token: str) -> str:
    words = [w for w in re.split(r"[_\-\s]+", token) if w]
    return " ".join(w.capitalize() if not w.isupper() or len(w) > 3 else w.title()
                    for w in words) or token
