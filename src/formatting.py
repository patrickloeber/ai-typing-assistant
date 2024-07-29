from typing import List


def to_bullet_points(*text: str) -> List[str]:
    return [f"    - {t}" for t in list(text)]
