from datetime import date


EASTER_JULIAN: int
EASTER_ORTHODOX: int
EASTER_WESTERN: int


def easter(year: int, method: int = 3) -> date: ...
